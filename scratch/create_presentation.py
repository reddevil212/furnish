import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_furnish_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6] # blank layout

    # Color Palette
    COLOR_BG_DARK = RGBColor(15, 23, 42)       # #0F172A (Deep Slate)
    COLOR_CARD_BG = RGBColor(30, 41, 59)       # #1E293B (Slate 800)
    COLOR_GOLD = RGBColor(245, 158, 11)        # #F59E0B (Amber Gold)
    COLOR_INDIGO = RGBColor(99, 102, 241)      # #6366F1 (Indigo Accent)
    COLOR_EMERALD = RGBColor(16, 185, 129)     # #10B981 (Emerald)
    COLOR_WHITE = RGBColor(248, 250, 252)      # #F8FAFC
    COLOR_MUTED = RGBColor(148, 163, 184)     # #94A3B8 (Slate 400)
    COLOR_CARD_BORDER = RGBColor(51, 65, 85)   # #334155

    def add_blank_slide_with_bg(bg_color=COLOR_BG_DARK):
        slide = prs.slides.add_slide(blank_slide_layout)
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = bg_color
        bg.line.fill.background()
        return slide

    def add_header(slide, title_text, category_text="FURNISH PROJECT PRESENTATION"):
        # Category tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_GOLD
        p_cat.font.name = "Arial"

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.733), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_WHITE
        p_title.font.name = "Arial"

        # Horizontal accent line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.55), Inches(11.733), Inches(0.03))
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_GOLD
        line.line.fill.background()

    def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
        return card

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    slide1 = add_blank_slide_with_bg()
    
    # Decorative Top Accent Bar
    accent_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = COLOR_GOLD
    accent_bar.line.fill.background()

    # Main Card
    add_card(slide1, 1.2, 1.2, 10.933, 5.1)

    tb = slide1.shapes.add_textbox(Inches(1.6), Inches(1.6), Inches(10.133), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "FURNISH"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = COLOR_GOLD
    p.font.name = "Arial"

    p2 = tf.add_paragraph()
    p2.text = "Next-Generation E-Commerce & Agentic AI Interior Stylist Platform"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(10)
    p2.font.name = "Arial"

    p3 = tf.add_paragraph()
    p3.text = "A modern full-stack web application powered by Django 6.1, Google AI Studio (Gemini 3.6 Flash), Autonomous Function Calling, and Razorpay Payments."
    p3.font.size = Pt(14)
    p3.font.color.rgb = COLOR_MUTED
    p3.space_before = Pt(15)
    p3.font.name = "Arial"

    # Badges row
    p4 = tf.add_paragraph()
    p4.text = "• Django 6.1  |  • Google Gemini 3.6 Flash  |  • 8 Database AI Tools  |  • Razorpay Payment Gateway"
    p4.font.size = Pt(13)
    p4.font.bold = True
    p4.font.color.rgb = COLOR_EMERALD
    p4.space_before = Pt(30)
    p4.font.name = "Arial"

    p5 = tf.add_paragraph()
    p5.text = "Project Technical Overview & Architecture Presentation"
    p5.font.size = Pt(12)
    p5.font.color.rgb = COLOR_MUTED
    p5.space_before = Pt(20)

    # ==========================================
    # SLIDE 2: Executive Summary & Vision
    # ==========================================
    slide2 = add_blank_slide_with_bg()
    add_header(slide2, "Executive Summary & Project Vision")

    # Card 1: E-Commerce Foundation
    add_card(slide2, 0.8, 1.8, 5.7, 5.0)
    tb = slide2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "🛒 Robust E-Commerce Foundation"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_GOLD

    bullets1 = [
        "Complete catalog management with dynamic multi-criteria filtering (category, price range, stock, featured).",
        "Seamless cart operations, wishlist management, and address book integration.",
        "Secure checkout with dual payment modes: Cash on Delivery (COD) & Razorpay Online Payment Gateway.",
        "UUID order tracking system with real-time status updates and order items breakdown."
    ]
    for b in bullets1:
        p_b = tf.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = COLOR_WHITE
        p_b.space_before = Pt(10)

    # Card 2: Innovation Layer
    add_card(slide2, 6.833, 1.8, 5.7, 5.0)
    tb = slide2.shapes.add_textbox(Inches(7.033), Inches(2.0), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "🤖 Agentic AI Innovation Layer"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_INDIGO

    bullets2 = [
        "Embedded AI Concierge powered by Google AI Studio (Gemini 3.6 Flash / Gemini models).",
        "Autonomous Tool Calling: 8 direct python tools interacting directly with Django ORM.",
        "Acts as a 24/7 personal interior stylist providing color matching, room layout advice, and catalog search.",
        "Can perform live actions: add/remove items to cart, retrieve active cart totals, and track past user orders."
    ]
    for b in bullets2:
        p_b = tf.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = COLOR_WHITE
        p_b.space_before = Pt(10)

    # ==========================================
    # SLIDE 3: Problem Statement & Solution
    # ==========================================
    slide3 = add_blank_slide_with_bg()
    add_header(slide3, "Problem Statement & The Furnish Solution")

    col_w = 3.64
    # Box 1: The Problem
    add_card(slide3, 0.8, 1.8, col_w, 5.0)
    tb = slide3.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(3.24), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "❌ The Problem"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = RGBColor(239, 68, 68) # Red
    prob_list = [
        "Traditional e-commerce feels rigid & static.",
        "Customers struggle to visual spatial fit & color harmony.",
        "High support load for simple queries like order tracking and product specs.",
        "Standard chatbots rely on dummy scripts and can't interact with the cart or catalog."
    ]
    for item in prob_list:
        p_item = tf.add_paragraph()
        p_item.text = "• " + item
        p_item.font.size = Pt(12)
        p_item.font.color.rgb = COLOR_MUTED
        p_item.space_before = Pt(10)

    # Box 2: The Solution
    add_card(slide3, 4.84, 1.8, col_w, 5.0)
    tb = slide3.shapes.add_textbox(Inches(5.04), Inches(2.0), Inches(3.24), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "💡 The Furnish Solution"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = COLOR_GOLD
    sol_list = [
        "Agentic AI assistant that reads live store inventory and database state.",
        "Autonomous function calling to query catalog, recommend pairings, and execute cart updates.",
        "Context-aware recommendations matching budget, stock, and style category.",
        "Instant self-service tracking for user orders directly in conversational UI."
    ]
    for item in sol_list:
        p_item = tf.add_paragraph()
        p_item.text = "• " + item
        p_item.font.size = Pt(12)
        p_item.font.color.rgb = COLOR_WHITE
        p_item.space_before = Pt(10)

    # Box 3: Key Benefits
    add_card(slide3, 8.88, 1.8, col_w, 5.0)
    tb = slide3.shapes.add_textbox(Inches(9.08), Inches(2.0), Inches(3.24), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🚀 Business Value"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = COLOR_EMERALD
    val_list = [
        "Higher conversion rates via personalized styling advice.",
        "Reduced friction & zero-click cart modifications.",
        "24/7 automated customer service with fallback local concierge.",
        "Modern aesthetic attracting premium home decor buyers."
    ]
    for item in val_list:
        p_item = tf.add_paragraph()
        p_item.text = "• " + item
        p_item.font.size = Pt(12)
        p_item.font.color.rgb = COLOR_WHITE
        p_item.space_before = Pt(10)

    # ==========================================
    # SLIDE 4: System Architecture
    # ==========================================
    slide4 = add_blank_slide_with_bg()
    add_header(slide4, "System Architecture & Technology Stack")

    # 4 Column Architecture Breakdown
    c_w = 2.7
    c_gap = 0.3
    start_x = 0.8

    arch_data = [
        ("🌐 Frontend Layer", COLOR_INDIGO, [
            "HTML5 & Responsive Layouts",
            "Custom Vanilla CSS Design System",
            "AJAX-driven AI Chat UI",
            "Dynamic Cart Badges & Cards",
            "Glassmorphism Visual Style"
        ]),
        ("⚡ Backend Engine", COLOR_GOLD, [
            "Django 6.1 (Python Framework)",
            "Django ORM Data Abstraction",
            "Gunicorn WSGI Server",
            "Whitenoise Static Asset Engine",
            "Session History Management"
        ]),
        ("🧠 Agentic AI Core", COLOR_EMERALD, [
            "Google AI Studio (Gemini 3.6)",
            "Autonomous Tool Declarations",
            "ContextVar Thread Safety",
            "Dual Mode: Gemini & Local Fallback",
            "Regex Token Matching Fallback"
        ]),
        ("💳 Payments & Data", RGBColor(236, 72, 153), [
            "Razorpay Payment Gateway",
            "HMAC SHA256 Verification",
            "PostgreSQL / SQLite Database",
            "UUID Order Tracking",
            "Pillow Image Processing"
        ])
    ]

    for idx, (title, color, items) in enumerate(arch_data):
        x = start_x + idx * (c_w + c_gap)
        add_card(slide4, x, 1.8, c_w, 5.0)
        tb = slide4.shapes.add_textbox(Inches(x + 0.15), Inches(2.0), Inches(c_w - 0.3), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = color
        for it in items:
            p_it = tf.add_paragraph()
            p_it.text = "▪ " + it
            p_it.font.size = Pt(11)
            p_it.font.color.rgb = COLOR_WHITE
            p_it.space_before = Pt(8)

    # ==========================================
    # SLIDE 5: Database Architecture & Models
    # ==========================================
    slide5 = add_blank_slide_with_bg()
    add_header(slide5, "Database Schema & Entity Models")

    # Table of models
    rows, cols = 7, 3
    left, top, width, height = Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.9)
    table_shape = slide5.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    # Set column widths
    table.columns[0].width = Inches(2.5)
    table.columns[1].width = Inches(4.5)
    table.columns[2].width = Inches(4.733)

    headers = ["Model Name", "Key Attributes", "Relationships & Purpose"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_CARD_BG
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_GOLD

    models_info = [
        ("Ecomm_Category", "category_name, category_slug, category_desc, category_image", "Organizes catalog into furniture types; auto-generates URL slugs."),
        ("Ecom_Product", "product_name, product_slug, price, quantity_in_stock, is_active, is_featured", "FK to Ecomm_Category; primary catalog table with stock controls."),
        ("Ecom_Favourites", "user, product, createdaAt", "FK to User & Product; user wishlist storage."),
        ("Ecom_Cart", "user, product, quantity, total_price (property)", "FK to User & Product; active shopping cart items with computed total."),
        ("Ecom_Adress", "user, address", "FK to User; stores shipping addresses for checkout."),
        ("Ecom_Order & Item", "order_id (UUID), user, shipping_address, total_amount, payment_mode, payment_status, razor_order_id", "FK to User & Address; stores completed/pending orders & items.")
    ]

    for r_idx, row_data in enumerate(models_info, start=1):
        for c_idx, text in enumerate(row_data):
            cell = table.cell(r_idx, c_idx)
            cell.text = text
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(24, 34, 53) if r_idx % 2 == 0 else COLOR_CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_WHITE if c_idx != 0 else COLOR_EMERALD
            if c_idx == 0:
                p.font.bold = True

    # ==========================================
    # SLIDE 6: Agentic AI Autonomous Tools
    # ==========================================
    slide6 = add_blank_slide_with_bg()
    add_header(slide6, "Deep Dive: Agentic AI Function Calling Architecture")

    add_card(slide6, 0.8, 1.8, 11.733, 5.0)

    tb = slide6.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "⚙️ 8 Autonomous Python Tools Exposed to Google Gemini"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_GOLD

    tools_grid = [
        ("1. search_products(query, category, min_price, max_price)", "Queries ORM catalog with fuzzy token-matching & stem relevance scoring."),
        ("2. get_product_details(product_name_or_id)", "Fetches complete specs, exact stock count, and high-res image link."),
        ("3. get_user_cart()", "Calculates live cart contents, itemized list, and current subtotal for auth user."),
        ("4. add_product_to_cart(product_id, quantity)", "Validates stock levels and adds item directly to user's cart in DB."),
        ("5. remove_product_from_cart(product_id)", "Deletes specified product from active user session cart."),
        ("6. get_order_history()", "Fetches top 5 recent orders placed by current user with delivery statuses."),
        ("7. track_specific_order(order_query)", "Performs UUID or tracking code lookup for exact order status."),
        ("8. get_store_categories()", "Returns all active categories and product counts for room styling suggestions.")
    ]

    for t_name, t_desc in tools_grid:
        p_t = tf.add_paragraph()
        p_t.text = f"• {t_name}"
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_EMERALD
        p_t.space_before = Pt(6)

        p_d = tf.add_paragraph()
        p_d.text = f"   └─ {t_desc}"
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = COLOR_MUTED

    # ==========================================
    # SLIDE 7: Thread Safety & Dual-Mode Agent
    # ==========================================
    slide7 = add_blank_slide_with_bg()
    add_header(slide7, "AI Architecture: ContextVar Isolation & Fallback Engine")

    # Card 1: ContextVar Isolation
    add_card(slide7, 0.8, 1.8, 5.7, 5.0)
    tb = slide7.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "🔒 Thread-Safe ContextVar Isolation"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = COLOR_INDIGO

    bullets_cv = [
        "Google GenAI SDK deep-copies tool declarations during schema registration.",
        "Furnish uses Python `contextvars.ContextVar('active_agent')` to bind the active web request instance.",
        "Allows top-level function declarations (`search_products()`) to seamlessly route tool executions to the current HTTP request user.",
        "Prevents cross-talk between concurrent web users and avoids thread locking issues."
    ]
    for b in bullets_cv:
        p_b = tf.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = COLOR_WHITE
        p_b.space_before = Pt(10)

    # Card 2: Local Concierge Fallback
    add_card(slide7, 6.833, 1.8, 5.7, 5.0)
    tb = slide7.shapes.add_textbox(Inches(7.033), Inches(2.0), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "🛡️ Local Concierge Fallback Engine"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = COLOR_GOLD

    bullets_fb = [
        "Activated automatically when API key is missing or quota/rate limit is reached (HTTP 429).",
        "Uses regex keyword extraction and stop-word filtering to perform local DB catalog searches.",
        "Supports full cart management (add, inspect, remove) locally.",
        "Tracks orders via regex pattern extraction on order UUIDs.",
        "Guarantees 100% service uptime even when external AI API services are unavailable."
    ]
    for b in bullets_fb:
        p_b = tf.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = COLOR_WHITE
        p_b.space_before = Pt(10)

    # ==========================================
    # SLIDE 8: Checkout & Razorpay Integration
    # ==========================================
    slide8 = add_blank_slide_with_bg()
    add_header(slide8, "E-Commerce Workflow & Razorpay Payments")

    # Workflow Steps
    steps = [
        ("Step 1: Product Selection", "Browse, filter, or ask AI Stylist to add products to cart.", COLOR_INDIGO),
        ("Step 2: Address & Order", "Select saved address or enter new address. Create order in DB.", COLOR_GOLD),
        ("Step 3: Razorpay Initialization", "Generate Razorpay order ID in backend (amount in paise).", COLOR_EMERALD),
        ("Step 4: HMAC Verification", "Client pays via Razorpay JS modal; signature verified with HMAC SHA256.", COLOR_GOLD),
        ("Step 5: Fulfillment & Tracking", "Cart flushed upon payment success; order assigned UUID tracking code.", COLOR_INDIGO)
    ]

    s_top = 1.8
    s_h = 0.9
    s_gap = 0.1
    for idx, (title, desc, color) in enumerate(steps):
        y = s_top + idx * (s_h + s_gap)
        add_card(slide8, 0.8, y, 11.733, s_h)
        tb = slide8.shapes.add_textbox(Inches(1.0), Inches(y + 0.1), Inches(11.333), Inches(0.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = color

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_WHITE

    # ==========================================
    # SLIDE 9: User Interface & Experience
    # ==========================================
    slide9 = add_blank_slide_with_bg()
    add_header(slide9, "UI/UX & Interactive Design System")

    # 3 Cards for UX
    ux_cards = [
        ("📱 Full-Page AI Studio", COLOR_GOLD, [
            "Dedicated `/ai/assistant/` route for full-screen interior styling experience.",
            "Interactive chat window with rich product recommendations rendered directly as actionable cards.",
            "Quick-action prompt buttons (e.g. 'Show Living Room Sofas', 'Track My Order')."
        ]),
        ("🛍️ Dynamic Catalog Page", COLOR_INDIGO, [
            "Multi-criteria filter sidebar (categories, price presets, price range, stock).",
            "Preserves active filter query strings during pagination.",
            "Visual badges for 'Featured' and 'Out of Stock' items."
        ]),
        ("⚡ Micro-Interactions", COLOR_EMERALD, [
            "Real-time cart item counter badge update.",
            "Instant toast notifications on adding to cart/favourites.",
            "Glassmorphic design elements with sleek dark mode aesthetics."
        ])
    ]

    for idx, (title, color, items) in enumerate(ux_cards):
        x = start_x + idx * (c_w + 0.3)
        add_card(slide9, x, 1.8, 3.64, 5.0)
        tb = slide9.shapes.add_textbox(Inches(x + 0.15), Inches(2.0), Inches(3.34), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color
        for it in items:
            p_it = tf.add_paragraph()
            p_it.text = "• " + it
            p_it.font.size = Pt(12)
            p_it.font.color.rgb = COLOR_WHITE
            p_it.space_before = Pt(10)

    # ==========================================
    # SLIDE 10: Performance & Security
    # ==========================================
    slide10 = add_blank_slide_with_bg()
    add_header(slide10, "Security Hardening & Performance Optimizations")

    add_card(slide10, 0.8, 1.8, 5.7, 5.0)
    tb = slide10.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "🔒 Security Controls"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_INDIGO

    sec_items = [
        "HMAC SHA256 Signature Verification for all Razorpay online payments.",
        "Django Built-in CSRF Protection across all POST endpoints (`@csrf_exempt` scoped strictly to Razorpay payment callback).",
        "User Session Authentication: Cart and order history locked behind auth guards.",
        "Environment variables management (`.env`) for secrets (GEMINI_API_KEY, RAZORPAY_KEY_SECRET)."
    ]
    for item in sec_items:
        p_item = tf.add_paragraph()
        p_item.text = "✓ " + item
        p_item.font.size = Pt(12)
        p_item.font.color.rgb = COLOR_WHITE
        p_item.space_before = Pt(10)

    add_card(slide10, 6.833, 1.8, 5.7, 5.0)
    tb = slide10.shapes.add_textbox(Inches(7.033), Inches(2.0), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "⚡ Performance Optimizations"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_EMERALD

    perf_items = [
        "Optimized ORM Queries: Extensive use of `select_related()` and `prefetch_related()` to eliminate N+1 queries.",
        "Database Aggregations: `Count()` annotations for active products per category.",
        "Whitenoise static asset compression and caching for production deployment.",
        "Pagination capped at 9 products per page for fast DOM rendering."
    ]
    for item in perf_items:
        p_item = tf.add_paragraph()
        p_item.text = "⚡ " + item
        p_item.font.size = Pt(12)
        p_item.font.color.rgb = COLOR_WHITE
        p_item.space_before = Pt(10)

    # ==========================================
    # SLIDE 11: Future Roadmap & Enhancements
    # ==========================================
    slide11 = add_blank_slide_with_bg()
    add_header(slide11, "Future Roadmap & Technical Expansion")

    roadmap = [
        ("Phase 1: AR Room Visualization", "Integrate WebXR / 3D model previews (GLTF/USDZ) allowing users to visually place furniture in their room using smartphone cameras.", COLOR_GOLD),
        ("Phase 2: Multimodal Visual AI Search", "Enable users to upload a picture of their room or inspiration photo; Gemini Vision API analyzes room style and recommends matching pieces.", COLOR_INDIGO),
        ("Phase 3: Conversational Voice Shopping", "Implement Web Speech API for real-time voice interaction with the AI Interior Stylist.", COLOR_EMERALD),
        ("Phase 4: Multi-Vendor & Analytics Dashboard", "Seller portal for inventory management and AI-driven sales analytics.", COLOR_GOLD)
    ]

    for idx, (title, desc, color) in enumerate(roadmap):
        y = s_top + idx * (1.1 + 0.1)
        add_card(slide11, 0.8, y, 11.733, 1.1)
        tb = slide11.shapes.add_textbox(Inches(1.0), Inches(y + 0.12), Inches(11.333), Inches(0.85))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = color

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_WHITE

    # ==========================================
    # SLIDE 12: Conclusion & Q&A
    # ==========================================
    slide12 = add_blank_slide_with_bg()
    
    # Accent line top
    accent_bar = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = COLOR_GOLD
    accent_bar.line.fill.background()

    add_card(slide12, 1.2, 1.2, 10.933, 5.1)

    tb = slide12.shapes.add_textbox(Inches(1.6), Inches(1.6), Inches(10.133), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Thank You!"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = COLOR_GOLD

    p2 = tf.add_paragraph()
    p2.text = "Furnish — Pioneering the Future of AI-Powered E-Commerce"
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(10)

    p3 = tf.add_paragraph()
    p3.text = "Key Takeaway: Furnish proves that integrating autonomous AI agents with full database tool execution creates a superior, frictionless shopping experience for modern users."
    p3.font.size = Pt(14)
    p3.font.color.rgb = COLOR_MUTED
    p3.space_before = Pt(20)

    p4 = tf.add_paragraph()
    p4.text = "Open for Questions & Live Demonstration"
    p4.font.size = Pt(18)
    p4.font.bold = True
    p4.font.color.rgb = COLOR_EMERALD
    p4.space_before = Pt(30)

    # Save output file
    output_path = os.path.join("c:\\Users\\sayan\\OneDrive\\Desktop\\internship2", "Furnish_Project_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    build_furnish_presentation()
