from .models import *

def cart_and_fav_counts(request):
    if request.user.is_authenticated:
        fav_count = Ecom_Favourites.objects.filter(user=request.user).count()
        cart_items = Ecom_Cart.objects.filter(user=request.user)
        cart_count = sum(item.quantity for item in cart_items)
    else:
        fav_count = 0
        cart_count = 0
    return {
        'fav_count': fav_count,
        'cart_count': cart_count,
    }


def get_all_categories(request):
    categories = Ecomm_Category.objects.all()
    return {
        'categories': categories
    }