from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Ecom_Product, Ecomm_Category

# Create your views here.

def home(request):
    
    return render(request, 'index.html')

def products(request):
    return render(request, 'products.html')

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
            return render(request, 'login.html', {'error': 'Please enter both username and password.'})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password.'})

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
            return render(request, 'register.html', {'error': 'All fields are required.'})

        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match.'})

        if User.objects.filter(username__iexact=username).exists():
            return render(request, 'register.html', {'error': 'Username is already taken.'})

        if User.objects.filter(email__iexact=email).exists():
            return render(request, 'register.html', {'error': 'An account with this email already exists.'})

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            auth_login(request, user)
            return redirect('home')
        except Exception as e:
            return render(request, 'register.html', {'error': 'An error occurred during registration. Please try again.'})

    return render(request, 'register.html')

def logout(request):
    auth_logout(request)
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

