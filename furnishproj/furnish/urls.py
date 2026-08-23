from django.urls import path
from .views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('home/', home_view, name='home_alt'),
    path('search/', search, name='search'),
    path('search/<str:query>/', search, name='search_with_query'),
    path('aboutus/', aboutus, name='aboutus'),
    path('about/', aboutus, name='about'),
    path('contact/', contact, name='contact'),
    path('products/', products, name='products'),
    path('testimonials/', testimonials, name='testimonials'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('product/<slug:pslug>', get_product_detail_view, name='get_product_detail_view'),
    path('category/<slug:cslug>', get_product_from_category, name='get_product_from_category'),
    path('favourites/', view_favourites, name='favourites'),
    path('add-to-favourites/<int:pid>/', add_to_fav, name='add_to_fav'),
    path('add-to-favourites/<int:userId>/<int:pid>/', add_to_fav, name='add_to_fav_alt'),
    path('remove-from-favourites/<int:pid>/', remove_from_fav, name='remove_from_fav'),
    path('cart/', view_cart, name='cart'),
    path('add-to-cart/<int:pid>/', add_to_cart, name='add_to_cart'),
    path('update-cart/<int:pid>/<str:action>/', update_cart_quantity, name='update_cart_quantity'),
    path('remove-from-cart/<int:pid>/', remove_from_cart, name='remove_from_cart'),
]

