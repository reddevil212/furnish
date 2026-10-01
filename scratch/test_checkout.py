import os
import sys

# Add furnishproj to path
sys.path.append(os.path.abspath('furnishproj'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'furnishproj.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from furnish.models import Ecomm_Category, Ecom_Product, Ecom_Cart, Ecom_Adress, Ecom_Order, Ecom_OrderItem

print("Testing Django setup...")

# Get or create a test user
user, created = User.objects.get_or_create(username="testuser", defaults={"email": "test@example.com"})
if created:
    user.set_password("password123")
    user.save()

# Get or create a category and product
category, _ = Ecomm_Category.objects.get_or_create(category_name="Test Category")
product, _ = Ecom_Product.objects.get_or_create(
    product_name="Test Table",
    defaults={
        "product_category": category,
        "product_price": 4999.00,
        "product_quantity_in_stock": 10,
        "product_description": "Test description"
    }
)

# Add to cart
cart_item, _ = Ecom_Cart.objects.get_or_create(user=user, product=product, defaults={"quantity": 1})

# Add address
address, _ = Ecom_Adress.objects.get_or_create(user=user, defaults={"address": "123 Test Street, City"})

client = Client()
client.force_login(user)

print("\n--- GET /checkout/ ---")
res = client.get('/checkout/')
print("Status code:", res.status_code)
if res.status_code != 200:
    print("Response content:", res.content.decode('utf-8'))

print("\n--- POST /order-process/ (COD) ---")
res_post = client.post('/order-process/', {
    'address_id': address.id,
    'payment_method': 'cod'
}, follow=True)
print("COD Redirect chain:", res_post.redirect_chain)
print("COD Status code:", res_post.status_code)
print("Orders count:", Ecom_Order.objects.filter(user=user).count())

print("\n--- Testing Online Payment ---")
# Re-add to cart for online payment test
Ecom_Cart.objects.get_or_create(user=user, product=product, defaults={"quantity": 1})
res_online = client.post('/order-process/', {
    'address_id': address.id,
    'payment_method': 'online'
}, follow=True)
print("Online Redirect chain:", res_online.redirect_chain)
print("Online Status code:", res_online.status_code)
