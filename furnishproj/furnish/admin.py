from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Ecomm_Category)
class EcommCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'category_slug', 'category_created_at')
    prepopulated_fields = {'category_slug': ('category_name',)}

@admin.register(Ecom_Product)
class EcomProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_category', 'product_price', 'product_quantity_in_stock', 'product_is_active')
    list_filter = ('product_category', 'product_is_active', 'product_created_at')
    search_fields = ('product_name', 'product_description')
    prepopulated_fields = {'product_slug': ('product_name',)}

admin.site.register(Ecom_Favourites)
admin.site.register(Ecom_Cart)
admin.site.register(Ecom_Order)
admin.site.register(Ecom_OrderItem)
