from django.urls import path
from .views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('home/', home_view, name='home_alt'),
    path('aboutus/', aboutus, name='aboutus'),
    path('about/', aboutus, name='about'),
    path('contact/', contact, name='contact'),
    path('products/', products, name='products'),
    path('testimonials/', testimonials, name='testimonials'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('product/<slug:pslug>', get_product_detail_view, name='get_product_detail_view'),
]

