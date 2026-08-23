from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import *

# Create your views here.



def products(request):
    products = Ecom_Product.objects.all()
    

    context = {
        'products': products
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


    
    return render(request, 'search.html')


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