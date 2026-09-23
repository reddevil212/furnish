import re
import json
import uuid
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponse, JsonResponse
from .models import *
from .ai_agent import FurnishAIAgent

# Create your views here.


def products(request):
    products_qs = Ecom_Product.objects.filter(product_is_active=True)

    # 1. Search Query
    q = request.GET.get('q', '').strip()
    if q:
        products_qs = products_qs.filter(
            Q(product_name__icontains=q) |
            Q(product_description__icontains=q) |
            Q(product_category__category_name__icontains=q)
        )

    # 2. Category Filter (supports multiple selected categories)
    selected_categories = [c for c in request.GET.getlist('category') if c]
    if selected_categories:
        products_qs = products_qs.filter(product_category__category_slug__in=selected_categories)

    # 3. Price Preset Filter
    price_range = request.GET.get('price_range', '').strip()
    if price_range == 'under_5000':
        products_qs = products_qs.filter(product_price__lt=5000)
    elif price_range == '5000_10000':
        products_qs = products_qs.filter(product_price__gte=5000, product_price__lte=10000)
    elif price_range == '10000_25000':
        products_qs = products_qs.filter(product_price__gte=10000, product_price__lte=25000)
    elif price_range == 'above_25000':
        products_qs = products_qs.filter(product_price__gt=25000)

    # Custom Min/Max Price
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    if min_price:
        try:
            products_qs = products_qs.filter(product_price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products_qs = products_qs.filter(product_price__lte=float(max_price))
        except ValueError:
            pass

    # 4. In Stock Filter
    in_stock = request.GET.get('in_stock', '').strip()
    if in_stock in ('1', 'true', 'on'):
        products_qs = products_qs.filter(product_quantity_in_stock__gt=0)

    # 5. Featured Filter
    featured = request.GET.get('featured', '').strip()
    if featured in ('1', 'true', 'on'):
        products_qs = products_qs.filter(product_is_featured=True)

    # 6. Sorting
    sort_by = request.GET.get('sort_by', 'featured').strip()
    if sort_by == 'price_asc':
        products_qs = products_qs.order_by('product_price')
    elif sort_by == 'price_desc':
        products_qs = products_qs.order_by('-product_price')
    elif sort_by == 'name_asc':
        products_qs = products_qs.order_by('product_name')
    elif sort_by == 'name_desc':
        products_qs = products_qs.order_by('-product_name')
    elif sort_by == 'newest':
        products_qs = products_qs.order_by('-product_created_at')
    elif sort_by == 'oldest':
        products_qs = products_qs.order_by('product_created_at')
    else:
        sort_by = 'featured'
        products_qs = products_qs.order_by('-product_is_featured', '-id')

    # Categories with count of active products
    categories_with_count = Ecomm_Category.objects.annotate(
        total_products=Count('products', filter=Q(products__product_is_active=True))
    ).filter(total_products__gt=0)

    # Compute active filter count
    active_filters_count = (
        len(selected_categories)
        + (1 if price_range or min_price or max_price else 0)
        + (1 if in_stock in ('1', 'true', 'on') else 0)
        + (1 if featured in ('1', 'true', 'on') else 0)
        + (1 if q else 0)
    )

    # Query string for preserving filters during pagination
    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    filter_querystring = params.urlencode()

    # Pagination: 9 products per page
    paginator = Paginator(products_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories_with_count': categories_with_count,
        'selected_categories': selected_categories,
        'price_range': price_range,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock': in_stock,
        'featured': featured,
        'sort_by': sort_by,
        'q': q,
        'active_filters_count': active_filters_count,
        'filter_querystring': filter_querystring,
        'total_count': paginator.count
    }
    return render(request, "products.html", context)

def contact(request):
    return render(request, 'contact.html')

def aboutus(request):
    return render(request, 'about.html')

def testimonials(request):
    return render(request, 'testimonials.html')

def login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')

    return render(request, 'login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not all([first_name, last_name, username, email, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'register.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'register.html')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            auth_login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return render(request, 'register.html')

    return render(request, 'register.html')


def change_password(request):
    if request.method == 'POST':
        curntPass=request.POST.get('curntPass')
        newPass=request.POST.get('newPass')
        confirm_password=request.POST.get('confirm_password')

        curntUser = request.user.username
        user = authenticate(request, username=curntUser, password=curntPass)
        if user is not None and newPass == confirm_password:
            user.set_password(newPass)
            user.save()
            messages.success(request, "Password Changed Sucessfully")

            auth_login(request, user)
            
        
        else:
            messages.error(request, "Something went Wrong")


    return render(request, 'password.html')

def logout(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def home_view(request):
    
    products = Ecom_Product.objects.all()
    


    context = {
        'products': products
    }
    return render(request, "index.html", context)

def get_product_detail_view(request,pslug):
    product = Ecom_Product.objects.filter(product_slug=pslug).first()
    related_products = Ecom_Product.objects.filter(product_category=product.product_category).exclude(id=product.id)[:4]
    context = {
        'product' : product,
        'related_products': related_products
    }
    return render(request, 'specific_product.html', context)


def get_product_from_category(request, cslug):
    category = Ecomm_Category.objects.filter(category_slug=cslug).first()
    if category:
        products = Ecom_Product.objects.filter(product_category=category) 
    else:
        products = []
    context = {
        'category': category,
        'products': products
    }
    return render(request, "category.html", context)

def search(request, query=None):
    if not query:
        query = request.GET.get('query', '')
    query = query.strip()

    if query:
        pattern = r'\b' + re.escape(query) + r'\b'
        searchedProducts = Ecom_Product.objects.filter(product_is_active=True).filter(
            Q(product_name__icontains=query) | 
            Q(product_category__category_name__icontains=query) |
            Q(product_description__iregex=pattern)
        ).distinct()
    else:
        searchedProducts = Ecom_Product.objects.none()

    context = {
        "searchedProducts": searchedProducts,
        "query": query
    }
    
    return render(request, 'search.html', context)




# ---------------- Favourites Views ----------------

def view_favourites(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to view your favourites.")
        return redirect('login')

    fav_items = Ecom_Favourites.objects.filter(user=request.user).select_related('product')
    return render(request, 'favourites.html', {'fav_items': fav_items})


def add_to_fav(request, pid, userId=None):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to add items to your favourites.")
        return redirect('login')

    product = Ecom_Product.objects.filter(id=pid).first()
    if not product:
        messages.error(request, "Product not found.")
        return redirect('home')

    fav, created = Ecom_Favourites.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f"'{product.product_name}' added to favourites.")
    else:
        messages.info(request, f"'{product.product_name}' is already in your favourites.")

    return redirect(request.META.get('HTTP_REFERER', 'favourites'))


def remove_from_fav(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')

    fav_item = Ecom_Favourites.objects.filter(user=request.user, product_id=pid).first()
    if fav_item:
        fav_item.delete()
        messages.success(request, "Item removed from favourites.")
    else:
        messages.error(request, "Item not found in favourites.")

    return redirect('favourites')


# ---------------- Cart Views ----------------

def view_cart(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to view your cart.")
        return redirect('login')

    cart_items = Ecom_Cart.objects.filter(user=request.user).select_related('product')
    total_amount = sum(item.total_price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
    }
    return render(request, 'cart.html', context)


def add_to_cart(request, pid):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to add items to your cart.")
        return redirect('login')

    product = Ecom_Product.objects.filter(id=pid).first()
    if not product:
        messages.error(request, "Product not found.")
        return redirect('home')

    quantity = 1
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

    cart_item, created = Ecom_Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f"Updated '{product.product_name}' quantity in cart.")
    else:
        messages.success(request, f"Added '{product.product_name}' to cart.")

    return redirect(request.META.get('HTTP_REFERER', 'cart'))


def update_cart_quantity(request, pid, action):
    if not request.user.is_authenticated:
        return redirect('login')

    cart_item = Ecom_Cart.objects.filter(user=request.user, product_id=pid).first()
    if cart_item:
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
                messages.info(request, "Item removed from cart.")

    return redirect('cart')


def remove_from_cart(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')

    cart_item = Ecom_Cart.objects.filter(user=request.user, product_id=pid).first()
    if cart_item:
        cart_item.delete()
        messages.success(request, "Item removed from cart.")

    return redirect('cart')


def manage_address_page(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to manage your addresses.")
        return redirect('login')

    user_addresses = Ecom_Adress.objects.filter(
        user=request.user
    )

    context = {
        'user_addresses': user_addresses
    }

    return render(request, 'address.html', context)


def add_address(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to add an address.")
        return redirect('login')

    if request.method == "POST":
        new_address = request.POST.get("address", "").strip()

        if not new_address:
            messages.error(request, "Please enter an address.")
            return redirect("manage_address_page")

        Ecom_Adress.objects.create(
            user=request.user,
            address=new_address
        )

        messages.success(request, "Address added successfully.")

    return redirect("manage_address_page")


def remove_address(request, address_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to remove an address.")
        return redirect('login')

    user = request.user
    adr = Ecom_Adress.objects.filter(id=address_id, user=user).first()

    if adr:
        adr.delete()
        messages.success(request, "Address removed successfully.")
    else:
        messages.error(request, 'Address not found to delete.')

    return redirect('manage_address_page')



def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to view your cart.")
        return redirect('login')

    cart_items = Ecom_Cart.objects.filter(user=request.user).select_related('product')
    total_amount = sum(item.total_price for item in cart_items)
    user_addresses = Ecom_Adress.objects.filter(
        user=request.user
    )
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'user_addresses': user_addresses
    }
    return render(request, 'checkout.html', context)


def order_process(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to place an order.")
        return redirect('login')

    if request.method == "POST":
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')

        cart_items = Ecom_Cart.objects.filter(user=request.user).select_related('product')
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart')

        if payment_method not in ['cod', 'online']:
            messages.error(request, "Please select a valid payment method.")
            return redirect('checkout')

        shipping_address = None
        if address_id:
            shipping_address = Ecom_Adress.objects.filter(id=address_id, user=request.user).first()

        if not shipping_address:
            messages.error(request, "Please select a valid delivery address.")
            return redirect('checkout')

        total_amount = sum(item.total_price for item in cart_items)
        tracking_number = f"{uuid.uuid4().hex[:8].upper()}"

        if payment_method == 'cod':
            order = Ecom_Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                total_amount=total_amount,
                payment_mode='cod',
                payment_status='pending',
                order_tracking_number=tracking_number
            )

            order_items = [
                Ecom_OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )
                for item in cart_items
            ]
            Ecom_OrderItem.objects.bulk_create(order_items)

            # Clear cart after successfully creating order & items
            cart_items.delete()

            messages.success(request, f"Order #{order.order_id} placed successfully with Cash on Delivery!")
            return redirect('orders')

        elif payment_method == 'online':
            order = Ecom_Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                total_amount=total_amount,
                payment_mode='online',
                payment_status='pending',
                order_tracking_number=tracking_number
            )

            order_items = [
                Ecom_OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )
                for item in cart_items
            ]
            Ecom_OrderItem.objects.bulk_create(order_items)

            # Create Razorpay Order
            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                amount_in_paise = int(total_amount * 100)
                razor_order = client.order.create({
                    'amount': amount_in_paise,
                    'currency': 'INR',
                    'payment_capture': '1',
                    'notes': {
                        'order_id': str(order.order_id),
                        'user_id': str(request.user.id),
                    }
                })
                order.razor_order_id = razor_order['id']
                order.save()
                return redirect('payment_page', order_id=order.order_id)
            except Exception as e:
                order.payment_status = 'failed'
                order.save()
                messages.error(request, f"Failed to initialize online payment: {str(e)}")
                return redirect('checkout')

    return redirect('checkout')


def payment_page(request, order_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to complete your payment.")
        return redirect('login')

    order = Ecom_Order.objects.filter(order_id=order_id, user=request.user).prefetch_related('item__product').select_related('shipping_address').first()
    if not order:
        messages.error(request, "Order not found.")
        return redirect('checkout')

    if order.payment_status == 'completed':
        messages.info(request, "This order has already been paid for.")
        return redirect('orders')

    amount_in_paise = int(order.total_amount * 100)
    context = {
        'order': order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': order.razor_order_id,
        'amount_in_paise': amount_in_paise,
    }
    return render(request, 'payment.html', context)


@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
            messages.error(request, "Incomplete payment details received.")
            return redirect('checkout')

        order = Ecom_Order.objects.filter(razor_order_id=razorpay_order_id).first()
        if not order:
            messages.error(request, "Order corresponding to this payment was not found.")
            return redirect('checkout')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            order.payment_status = 'completed'
            order.razor_payment_id = razorpay_payment_id
            order.razorpay_signeture = razorpay_signature
            order.save()

            # Clear user cart on successful payment
            Ecom_Cart.objects.filter(user=order.user).delete()

            messages.success(request, f"Payment successful! Order #{order.order_id} has been confirmed.")
            return redirect('orders')
        except razorpay.errors.SignatureVerificationError:
            order.payment_status = 'failed'
            order.save()
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect('checkout')
        except Exception as e:
            order.payment_status = 'failed'
            order.save()
            messages.error(request, f"An error occurred during payment processing: {str(e)}")
            return redirect('checkout')

    return redirect('checkout')


def orders(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to view your orders.")
        return redirect('login')

    user_orders = Ecom_Order.objects.filter(user=request.user).prefetch_related('item__product').select_related('shipping_address').order_by('-id')

    context = {
        'orders': user_orders
    }
    return render(request, 'orders.html', context)


# =====================================================================
# Agentic AI Views (Powered by Google AI Studio API)
# =====================================================================

def ai_chat_view(request):
    """
    Handles user chat interaction with Furnish Agentic AI.
    Executes tool calling (search, cart updates, order tracking) and returns
    structured JSON with conversational text, rich product cards, and cart stats.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST method is allowed."}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    user_message = data.get("message", "").strip()
    if not user_message:
        return JsonResponse({"status": "error", "message": "Message cannot be empty."}, status=400)

    # Retrieve conversational history from session
    session_history = request.session.get("furnish_ai_chat_history", [])

    # Instantiate Agent and execute multi-turn agentic cycle
    agent = FurnishAIAgent(request=request)
    result = agent.chat(user_message, session_history=session_history)

    # Save updated history
    request.session["furnish_ai_chat_history"] = result.get("history", [])
    request.session.modified = True

    return JsonResponse(result)


def ai_clear_history_view(request):
    """Clears the AI session chat history."""
    if request.method == "POST":
        request.session["furnish_ai_chat_history"] = []
        request.session.modified = True
        return JsonResponse({"status": "success", "message": "Chat history cleared."})
    return JsonResponse({"status": "error", "message": "POST required."}, status=405)


def ai_assistant_page(request):
    """Renders the dedicated full-page AI Interior Studio & Concierge experience."""
    featured_products = Ecom_Product.objects.filter(product_is_active=True, product_is_featured=True)[:4]
    categories = Ecomm_Category.objects.all()
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, "ai_assistant.html", context)
