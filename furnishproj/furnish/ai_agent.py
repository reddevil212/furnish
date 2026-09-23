import os
import re
import json
import logging
import contextvars
from django.conf import settings
from django.db.models import Q
from .models import Ecom_Product, Ecomm_Category, Ecom_Cart, Ecom_Order, Ecom_OrderItem

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

_active_agent = contextvars.ContextVar("active_agent", default=None)

# Top-level tool functions for Google GenAI tool declarations (deepcopied cleanly without thread-locks)
def search_products(query: str = "", category: str = "", min_price: float = None, max_price: float = None, in_stock_only: bool = True) -> str:
    """Search the Furnish catalog for furniture and decor products by keyword, category, and price range."""
    agent = _active_agent.get()
    return agent.search_products(query, category, min_price, max_price, in_stock_only) if agent else "{}"

def get_product_details(product_name_or_id: str) -> str:
    """Get complete specifications, stock, price, and category for a specific product."""
    agent = _active_agent.get()
    return agent.get_product_details(product_name_or_id) if agent else "{}"

def get_user_cart() -> str:
    """Fetch the current user's shopping cart contents, quantities, and subtotal."""
    agent = _active_agent.get()
    return agent.get_user_cart() if agent else "{}"

def add_product_to_cart(product_id: int, quantity: int = 1) -> str:
    """Add a specific product to the user's shopping cart."""
    agent = _active_agent.get()
    return agent.add_product_to_cart(product_id, quantity) if agent else "{}"

def remove_product_from_cart(product_id: int) -> str:
    """Remove a product from the user's shopping cart."""
    agent = _active_agent.get()
    return agent.remove_product_from_cart(product_id) if agent else "{}"

def get_order_history() -> str:
    """Retrieve recent orders and order statuses placed by the authenticated user."""
    agent = _active_agent.get()
    return agent.get_order_history() if agent else "{}"

def track_specific_order(order_query: str) -> str:
    """Track a specific order by UUID or tracking number."""
    agent = _active_agent.get()
    return agent.track_specific_order(order_query) if agent else "{}"

def get_store_categories() -> str:
    """Retrieve all furniture and decor categories available in Furnish."""
    agent = _active_agent.get()
    return agent.get_store_categories() if agent else "{}"


class FurnishAIAgent:
    """
    Agentic AI Concierge & Interior Stylist for Furnish.
    Uses Google AI Studio API (Gemini) with autonomous tool/function calling.
    """

    SYSTEM_INSTRUCTION = """You are the official AI Interior Stylist & Shopping Concierge for "Furnish" (a premium furniture and home decor e-commerce store).
Your goals:
1. Provide expert interior styling advice, color coordination tips, and room design ideas (e.g., Living Room, Bedroom, Dining, Office).
2. Autonomously use your provided tools to search catalog products, check stock, look up details, manage the user's cart, and check order statuses.
3. When recommending furniture, always call `search_products` or `get_store_categories` to suggest real items from our store.
4. When a user asks to add or remove an item to their cart, call `add_product_to_cart` or `remove_product_from_cart`.
5. When a user asks about their order or tracking, call `get_order_history` or `track_specific_order`.
6. Keep your answers warm, elegant, helpful, and concise. Use markdown (bullet points, bold product names, prices with ₹ or the store currency).
7. If the user is a guest (not logged in) and tries to view orders or modify a personal cart, gently remind them to log in or register.
"""

    def __init__(self, request=None):
        self.user = request.user if request and hasattr(request, 'user') else None
        self.api_key = (getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')).strip()
        self.model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-3.6-flash') or 'gemini-3.6-flash'
        
        # Execution context for rich UI payloads returned to frontend
        self.context = {
            'products': [],
            'cart_action': None,
            'orders': [],
            'cart_count': self._get_current_cart_count()
        }

        self.client = None
        if GENAI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Google GenAI Client: {e}")
                self.client = None

    def _get_current_cart_count(self):
        if self.user and self.user.is_authenticated:
            return sum(item.quantity for item in Ecom_Cart.objects.filter(user=self.user))
        return 0

    # -------------------------------------------------------------
    # Agent Tools (Registered with Gemini Function Calling)
    # -------------------------------------------------------------

    def search_products(self, query: str = "", category: str = "", min_price: float = None, max_price: float = None, in_stock_only: bool = True) -> str:
        """Search the Furnish catalog for furniture and decor products by keyword, category, and price range.
        
        Args:
            query: Keyword search term (e.g., 'sofa', 'dining table', 'wooden chair', 'bed').
            category: Optional category name to filter by.
            min_price: Minimum price filter.
            max_price: Maximum price filter.
            in_stock_only: If True, only returns products currently in stock.
            
        Returns:
            JSON summary of matching products including id, name, price, stock, and description.
        """
        qs = Ecom_Product.objects.filter(product_is_active=True)

        if in_stock_only:
            qs = qs.filter(product_quantity_in_stock__gt=0)

        if category:
            qs = qs.filter(product_category__category_name__icontains=category)

        if query:
            q_trimmed = query.strip()
            tokens = [w for w in re.split(r'\s+', q_trimmed) if len(w) > 2]
            if tokens:
                token_filter = Q()
                for token in tokens:
                    t_q = Q(product_name__icontains=token) | Q(product_description__icontains=token) | Q(product_category__category_name__icontains=token)
                    if token.endswith('s') and len(token) > 3:
                        singular = token[:-1]
                        t_q |= Q(product_name__icontains=singular) | Q(product_description__icontains=singular)
                    elif token.endswith('es') and len(token) > 4:
                        singular = token[:-2]
                        t_q |= Q(product_name__icontains=singular) | Q(product_description__icontains=singular)
                    token_filter |= t_q
                qs = qs.filter(token_filter)
            else:
                qs = qs.filter(
                    Q(product_name__icontains=q_trimmed) |
                    Q(product_description__icontains=q_trimmed) |
                    Q(product_category__category_name__icontains=q_trimmed)
                )

        if min_price is not None:
            qs = qs.filter(product_price__gte=min_price)

        if max_price is not None:
            qs = qs.filter(product_price__lte=max_price)

        products = list(qs.distinct()[:12])
        # Sort by relevance: title or category match comes first
        if query:
            tokens = [w for w in re.split(r'\s+', query.lower()) if len(w) > 2]
            stems = []
            for t in tokens:
                stems.append(t)
                if t.endswith('s') and len(t) > 3:
                    stems.append(t[:-1])
                elif t.endswith('es') and len(t) > 4:
                    stems.append(t[:-2])

            def relevance_score(prod):
                score = 0
                p_name = prod.product_name.lower()
                c_name = prod.product_category.category_name.lower() if prod.product_category else ""
                for s in stems:
                    if s in p_name:
                        score += 10
                    if s in c_name:
                        score += 8
                return score

            products.sort(key=relevance_score, reverse=True)
            # Filter out products with 0 score if at least one product has positive score
            if any(relevance_score(p) > 0 for p in products):
                products = [p for p in products if relevance_score(p) > 0]
            products = products[:8]

        results = []
        for p in products:
            item_data = {
                'id': p.id,
                'name': p.product_name,
                'slug': p.product_slug,
                'price': float(p.product_price),
                'stock': p.product_quantity_in_stock,
                'category': p.product_category.category_name if p.product_category else "General",
                'image_url': p.product_image.url if p.product_image else "/static/assets/images/placeholder.jpg",
                'description': p.product_description[:160] + "..." if len(p.product_description) > 160 else p.product_description
            }
            results.append(item_data)
            # Add to agent context if not already added
            if not any(existing['id'] == p.id for existing in self.context['products']):
                self.context['products'].append(item_data)

        if not results:
            return json.dumps({"status": "no_results", "message": f"No products found matching query='{query}' and category='{category}'."})

        return json.dumps({"status": "success", "count": len(results), "products": results})

    def get_product_details(self, product_name_or_id: str) -> str:
        """Get complete specifications, stock, price, and category for a specific product.
        
        Args:
            product_name_or_id: The ID or title/name of the product.
            
        Returns:
            JSON object containing full product specifications.
        """
        p = None
        if str(product_name_or_id).isdigit():
            p = Ecom_Product.objects.filter(id=int(product_name_or_id)).first()

        if not p:
            p = Ecom_Product.objects.filter(product_name__icontains=str(product_name_or_id)).first()

        if not p:
            p = Ecom_Product.objects.filter(product_slug__icontains=str(product_name_or_id)).first()

        if not p:
            return json.dumps({"status": "not_found", "message": f"Product '{product_name_or_id}' not found."})

        data = {
            'id': p.id,
            'name': p.product_name,
            'slug': p.product_slug,
            'price': float(p.product_price),
            'stock': p.product_quantity_in_stock,
            'category': p.product_category.category_name if p.product_category else "",
            'image_url': p.product_image.url if p.product_image else "/static/assets/images/placeholder.jpg",
            'description': p.product_description
        }
        if not any(existing['id'] == p.id for existing in self.context['products']):
            self.context['products'].append(data)

        return json.dumps({"status": "success", "product": data})

    def get_user_cart(self) -> str:
        """Fetch the current user's shopping cart contents, quantities, and subtotal.
        
        Returns:
            JSON summary of all items in cart, individual prices, and subtotal.
        """
        if not self.user or not self.user.is_authenticated:
            return json.dumps({
                "status": "unauthenticated",
                "message": "User is not logged in. Please inform the user they must log in to view their cart."
            })

        cart_items = Ecom_Cart.objects.filter(user=self.user).select_related('product')
        items = []
        subtotal = 0.0
        for item in cart_items:
            item_total = float(item.total_price)
            subtotal += item_total
            items.append({
                'product_id': item.product.id,
                'name': item.product.product_name,
                'price': float(item.product.product_price),
                'quantity': item.quantity,
                'item_total': item_total,
                'image_url': item.product.product_image.url if item.product.product_image else ""
            })

        self.context['cart_count'] = sum(i['quantity'] for i in items)
        return json.dumps({
            "status": "success",
            "item_count": len(items),
            "total_units": self.context['cart_count'],
            "subtotal": subtotal,
            "items": items
        })

    def add_product_to_cart(self, product_id: int, quantity: int = 1) -> str:
        """Add a specific product to the user's shopping cart.
        
        Args:
            product_id: The numeric ID of the product to add.
            quantity: Quantity to add (default is 1).
            
        Returns:
            JSON result confirming whether item was added, with updated cart totals.
        """
        if not self.user or not self.user.is_authenticated:
            return json.dumps({
                "status": "unauthenticated",
                "message": "User is not logged in. Cart operations require logging in. Suggest the user to log in or register."
            })

        product = Ecom_Product.objects.filter(id=product_id).first()
        if not product:
            return json.dumps({"status": "error", "message": f"Product with ID {product_id} not found."})

        if product.product_quantity_in_stock < quantity:
            return json.dumps({
                "status": "insufficient_stock",
                "message": f"Only {product.product_quantity_in_stock} unit(s) available for '{product.product_name}'."
            })

        cart_item, created = Ecom_Cart.objects.get_or_create(
            user=self.user,
            product=product,
            defaults={'quantity': max(1, quantity)}
        )
        if not created:
            cart_item.quantity += max(1, quantity)
            cart_item.save()

        new_cart_count = self._get_current_cart_count()
        self.context['cart_count'] = new_cart_count
        self.context['cart_action'] = {
            'action': 'added',
            'product_id': product.id,
            'product_name': product.product_name,
            'quantity': cart_item.quantity,
            'new_cart_count': new_cart_count
        }

        return json.dumps({
            "status": "success",
            "message": f"Added {quantity}x '{product.product_name}' to cart.",
            "product_name": product.product_name,
            "quantity": cart_item.quantity,
            "new_cart_count": new_cart_count
        })

    def remove_product_from_cart(self, product_id: int) -> str:
        """Remove a product from the user's shopping cart.
        
        Args:
            product_id: The numeric ID of the product to remove.
            
        Returns:
            JSON confirmation of removal.
        """
        if not self.user or not self.user.is_authenticated:
            return json.dumps({
                "status": "unauthenticated",
                "message": "User is not logged in."
            })

        cart_item = Ecom_Cart.objects.filter(user=self.user, product_id=product_id).first()
        if not cart_item:
            return json.dumps({"status": "error", "message": "Product is not in the cart."})

        product_name = cart_item.product.product_name
        cart_item.delete()

        new_cart_count = self._get_current_cart_count()
        self.context['cart_count'] = new_cart_count
        self.context['cart_action'] = {
            'action': 'removed',
            'product_id': product_id,
            'product_name': product_name,
            'new_cart_count': new_cart_count
        }

        return json.dumps({
            "status": "success",
            "message": f"Removed '{product_name}' from your cart.",
            "new_cart_count": new_cart_count
        })

    def get_order_history(self) -> str:
        """Retrieve recent orders and order statuses placed by the authenticated user.
        
        Returns:
            JSON list of user's past orders, delivery status, and items.
        """
        if not self.user or not self.user.is_authenticated:
            return json.dumps({
                "status": "unauthenticated",
                "message": "User is not logged in. Orders are private and require user login."
            })

        orders = Ecom_Order.objects.filter(user=self.user).prefetch_related('item__product').order_by('-id')[:5]
        if not orders.exists():
            return json.dumps({"status": "empty", "message": "You haven't placed any orders yet."})

        results = []
        for o in orders:
            items_list = [f"{item.product.product_name} (x{item.quantity})" for item in o.item.all()]
            order_data = {
                'order_id': str(o.order_id),
                'tracking_number': o.order_tracking_number or "Processing",
                'payment_status': o.payment_status,
                'payment_mode': o.payment_mode,
                'total_amount': float(o.total_amount),
                'placed_at': str(o.order_placed_at),
                'items': items_list
            }
            results.append(order_data)
            self.context['orders'].append(order_data)

        return json.dumps({"status": "success", "orders": results})

    def track_specific_order(self, order_query: str) -> str:
        """Track a specific order by UUID or tracking number.
        
        Args:
            order_query: Order UUID or tracking code.
            
        Returns:
            JSON tracking status and details.
        """
        if not self.user or not self.user.is_authenticated:
            return json.dumps({"status": "unauthenticated", "message": "Please log in to track your order."})

        query_clean = order_query.strip()
        o = Ecom_Order.objects.filter(
            user=self.user
        ).filter(
            Q(order_id__icontains=query_clean) | Q(order_tracking_number__icontains=query_clean)
        ).first()

        if not o:
            return json.dumps({"status": "not_found", "message": f"Could not find an order matching '{order_query}' for your account."})

        items_list = [f"{item.product.product_name} (x{item.quantity})" for item in o.item.all()]
        order_data = {
            'order_id': str(o.order_id),
            'tracking_number': o.order_tracking_number or "In Transit / Processing",
            'payment_status': o.payment_status,
            'payment_mode': o.payment_mode,
            'total_amount': float(o.total_amount),
            'placed_at': str(o.order_placed_at),
            'items': items_list
        }
        self.context['orders'].append(order_data)
        return json.dumps({"status": "success", "order": order_data})

    def get_store_categories(self) -> str:
        """Retrieve all furniture and decor categories available in Furnish.
        
        Returns:
            JSON list of categories with product counts.
        """
        categories = Ecomm_Category.objects.all()
        data = [{'id': c.id, 'name': c.category_name, 'slug': c.category_slug, 'product_count': c.products.count()} for c in categories]
        return json.dumps({"status": "success", "categories": data})

    # -------------------------------------------------------------
    # Agent Execution Loop
    # -------------------------------------------------------------

    def chat(self, user_message: str, session_history: list = None) -> dict:
        """Process user message using Google AI Studio API with tools, or fallback agentically."""
        if session_history is None:
            session_history = []

        # If Gemini client is available, run Google AI Studio model with tools
        if self.client:
            try:
                return self._chat_with_gemini(user_message, session_history)
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    note = "Google AI Studio free rate-limit/quota reached. Operating in Local Concierge Mode with catalog & cart tools active."
                else:
                    note = f"Gemini API connection notice. Operating in Local Concierge Mode with full catalog search & cart tools."
                logger.warning(f"Gemini API note: {e}")
                return self._chat_fallback(user_message, session_history, error_note=note)

        # Fallback local agent mode if API key not configured yet
        return self._chat_fallback(
            user_message, 
            session_history,
            error_note="Google AI Studio API key not configured in `.env`. Running in Local Concierge Mode with catalog & cart tools active."
        )

    def _chat_with_gemini(self, user_message: str, session_history: list) -> dict:
        """Calls Google AI Studio Gemini model with autonomous tool calling."""
        tools = [
            search_products,
            get_product_details,
            get_user_cart,
            add_product_to_cart,
            remove_product_from_cart,
            get_order_history,
            track_specific_order,
            get_store_categories
        ]

        # Build history contents
        history_contents = []
        for msg in session_history[-10:]:
            role = "user" if msg.get("role") == "user" else "model"
            text = msg.get("content", "")
            if text:
                history_contents.append(types.Content(role=role, parts=[types.Part.from_text(text=text)]))

        model_name = self.model_name
        config = types.GenerateContentConfig(
            system_instruction=self.SYSTEM_INSTRUCTION,
            tools=tools,
            temperature=0.6,
        )

        ctx_token = _active_agent.set(self)
        try:
            try:
                chat = self.client.chats.create(
                    model=model_name,
                    config=config,
                    history=history_contents
                )
                response = chat.send_message(user_message)
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    raise e
                logger.info(f"Retrying with gemini-flash-latest: {e}")
                model_name = "gemini-flash-latest"
                chat = self.client.chats.create(
                    model=model_name,
                    config=config,
                    history=history_contents
                )
                response = chat.send_message(user_message)
        finally:
            _active_agent.reset(ctx_token)

        bot_reply = response.text or "I've checked our Furnish collection for you! Here are the best options."

        # Update history
        updated_history = list(session_history)
        updated_history.append({"role": "user", "content": user_message})
        updated_history.append({"role": "assistant", "content": bot_reply})

        return {
            "status": "success",
            "message": bot_reply,
            "products": self.context['products'],
            "cart_action": self.context['cart_action'],
            "orders": self.context['orders'],
            "cart_count": self.context['cart_count'],
            "history": updated_history[-14:],
            "source": "gemini",
            "model": model_name
        }

    def _chat_fallback(self, user_message: str, session_history: list, error_note: str = "") -> dict:
        """Intelligent agentic fallback when Google AI Studio API key is missing or offline."""
        msg_lower = user_message.lower()
        bot_reply = ""

        # 1. Order Tracking
        if "order" in msg_lower or "track" in msg_lower:
            words = user_message.split()
            potential_ids = [w for w in words if len(w) > 4 and any(c.isdigit() for c in w)]
            if potential_ids:
                res = json.loads(self.track_specific_order(potential_ids[0]))
                if res.get("status") == "success":
                    bot_reply = f"Here is the status for your order **#{res['order']['order_id'][:8]}...**:\n- **Status**: {res['order']['tracking_number']}\n- **Payment**: {res['order']['payment_status'].capitalize()}\n- **Total**: ₹{res['order']['total_amount']}"
                else:
                    bot_reply = res.get("message", "Could not locate that order.")
            else:
                res = json.loads(self.get_order_history())
                if res.get("status") == "success":
                    bot_reply = f"You have **{len(res['orders'])} recent orders**:\n"
                    for o in res['orders']:
                        bot_reply += f"- **Order #{o['order_id'][:8]}**: ₹{o['total_amount']} ({o['payment_status']})\n"
                elif res.get("status") == "unauthenticated":
                    bot_reply = "Please [log in](/login/) to view and track your orders."
                else:
                    bot_reply = "You don't have any past orders yet. Browse our products to find your first piece!"

        # 2. Cart Operations
        elif "cart" in msg_lower:
            if "add" in msg_lower or "buy" in msg_lower:
                found = Ecom_Product.objects.filter(product_is_active=True)
                target = None
                for p in found:
                    if p.product_name.lower() in msg_lower:
                        target = p
                        break
                if target:
                    res = json.loads(self.add_product_to_cart(target.id, 1))
                    if res.get("status") == "success":
                        bot_reply = f"✓ Added **{target.product_name}** to your cart! You now have {res.get('new_cart_count')} items in your cart."
                    else:
                        bot_reply = res.get("message")
                else:
                    bot_reply = "Which item would you like to add to your cart? You can click the **Add to Cart** button on any product card below!"
                    self.search_products(query="")
            elif "remove" in msg_lower or "delete" in msg_lower:
                bot_reply = "You can manage and remove items directly in your [Shopping Cart](/cart/)."
            else:
                res = json.loads(self.get_user_cart())
                if res.get("status") == "success":
                    if res.get("item_count", 0) > 0:
                        bot_reply = f"Your shopping cart has **{res['total_units']} item(s)** (Subtotal: ₹{res['subtotal']:.2f}):\n"
                        for it in res['items']:
                            bot_reply += f"- **{it['name']}** x{it['quantity']} (₹{it['item_total']:.2f})\n"
                        bot_reply += "\nReady to order? Head to [Checkout](/checkout/)!"
                    else:
                        bot_reply = "Your cart is currently empty. Let me know what room or style you're looking to furnish!"
                elif res.get("status") == "unauthenticated":
                    bot_reply = "Please [log in](/login/) to view your cart items."

        # 3. Product Search & Interior Suggestions
        else:
            cleaned_query = re.sub(r'[^\w\s]', '', msg_lower)
            stop_words = {'show', 'me', 'find', 'looking', 'for', 'a', 'an', 'the', 'i', 'want', 'need', 'recommend', 'suggest', 'can', 'you', 'please', 'give', 'best', 'some'}
            keywords = [w for w in cleaned_query.split() if w not in stop_words]
            search_term = " ".join(keywords[:3]) if keywords else ""

            res = json.loads(self.search_products(query=search_term))
            if res.get("status") == "success" and res.get("count", 0) > 0:
                bot_reply = f"I've curated these pieces from our catalog for you:\n"
                for p in res['products'][:3]:
                    bot_reply += f"- **{p['name']}** (₹{p['price']}) — {p['category']}\n"
                bot_reply += "\nClick **Add to Cart** on any card below, or let me know if you need pairing advice!"
            else:
                cat_res = json.loads(self.get_store_categories())
                cats = [c['name'] for c in cat_res.get('categories', [])]
                bot_reply = f"Welcome to **Furnish Interior Assistant**! I can help you style your home, recommend furniture, add items to your cart, or track orders.\n\nExplore our categories: **{', '.join(cats) if cats else 'Sofas, Tables, Chairs'}**."

        if error_note:
            bot_reply += f"\n\n> *Note: {error_note}*"

        updated_history = list(session_history)
        updated_history.append({"role": "user", "content": user_message})
        updated_history.append({"role": "assistant", "content": bot_reply})

        return {
            "status": "success",
            "message": bot_reply,
            "products": self.context['products'],
            "cart_action": self.context['cart_action'],
            "orders": self.context['orders'],
            "cart_count": self.context['cart_count'],
            "history": updated_history[-14:],
            "source": "local_agent"
        }
