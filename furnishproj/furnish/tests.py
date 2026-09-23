import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Ecomm_Category, Ecom_Product, Ecom_Cart

class SearchTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Ecomm_Category.objects.create(category_name="Living Room")
        self.product1 = Ecom_Product.objects.create(
            product_category=self.category,
            product_name="Wooden Coffee Table",
            product_description="A sturdy wooden table",
            product_price=1500.00,
            product_quantity_in_stock=10
        )
        self.product2 = Ecom_Product.objects.create(
            product_category=self.category,
            product_name="Modern Armchair",
            product_description="Comfortable fabric chair",
            product_price=2500.00,
            product_quantity_in_stock=5
        )

    def test_search_base_url_status_code(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)

    def test_search_query_param(self):
        response = self.client.get(reverse('search') + '?query=Table')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wooden Coffee Table")
        self.assertNotContains(response, "Modern Armchair")

    def test_search_path_query(self):
        response = self.client.get(reverse('search_with_query', kwargs={'query': 'Armchair'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Modern Armchair")
        self.assertNotContains(response, "Wooden Coffee Table")


from django.contrib.auth.models import User
from .models import Ecom_Adress

class AddressTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', password='password123')

    def test_manage_address_unauthenticated(self):
        response = self.client.get(reverse('manage_address_page'))
        self.assertRedirects(response, reverse('login'))

    def test_manage_address_authenticated(self):
        self.client.login(username='testuser', password='password123')
        Ecom_Adress.objects.create(user=self.user, address="123 Main St")
        response = self.client.get(reverse('manage_address_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "123 Main St")

    def test_add_address(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('add_address'), {'address': '456 Oak Ave'})
        self.assertRedirects(response, reverse('manage_address_page'))
        self.assertTrue(Ecom_Adress.objects.filter(user=self.user, address='456 Oak Ave').exists())

    def test_add_empty_address(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('add_address'), {'address': '   '})
        self.assertRedirects(response, reverse('manage_address_page'))
        self.assertEqual(Ecom_Adress.objects.filter(user=self.user).count(), 0)

    def test_remove_address(self):
        self.client.login(username='testuser', password='password123')
        address = Ecom_Adress.objects.create(user=self.user, address="789 Pine Rd")
        response = self.client.get(reverse('remove_address', kwargs={'address_id': address.id}))
        self.assertRedirects(response, reverse('manage_address_page'))
        self.assertFalse(Ecom_Adress.objects.filter(id=address.id).exists())

    def test_remove_other_user_address(self):
        self.client.login(username='testuser', password='password123')
        other_address = Ecom_Adress.objects.create(user=self.other_user, address="101 Maple St")
        response = self.client.get(reverse('remove_address', kwargs={'address_id': other_address.id}))
        self.assertRedirects(response, reverse('manage_address_page'))
        self.assertTrue(Ecom_Adress.objects.filter(id=other_address.id).exists())


class AgenticAITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='stylistuser', password='password123')
        self.category = Ecomm_Category.objects.create(category_name="Bedroom")
        self.product = Ecom_Product.objects.create(
            product_category=self.category,
            product_name="King Size Velvet Bed",
            product_description="Plush luxury velvet bed frame",
            product_price=45000.00,
            product_quantity_in_stock=8
        )

    def test_ai_assistant_page(self):
        response = self.client.get(reverse('ai_assistant'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Interior Stylist")

    def test_ai_chat_endpoint_search(self):
        response = self.client.post(
            reverse('ai_chat'),
            data=json.dumps({'message': 'Show me beds'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('message', data)
        self.assertTrue(len(data.get('products', [])) > 0)
        self.assertEqual(data['products'][0]['name'], "King Size Velvet Bed")

    def test_ai_chat_cart_operation_authenticated(self):
        self.client.login(username='stylistuser', password='password123')
        response = self.client.post(
            reverse('ai_chat'),
            data=json.dumps({'message': f'Add {self.product.product_name} to my cart'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        # Check cart in db
        self.assertTrue(Ecom_Cart.objects.filter(user=self.user, product=self.product).exists())

    def test_ai_clear_history(self):
        # First send a message to set session
        self.client.post(
            reverse('ai_chat'),
            data=json.dumps({'message': 'Hello AI'}),
            content_type='application/json'
        )
        # Clear history
        response = self.client.post(reverse('ai_clear'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('status'), 'success')
        self.assertEqual(self.client.session.get('furnish_ai_chat_history'), [])


class ProductFilterTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat_sofa = Ecomm_Category.objects.create(category_name="Sofa")
        self.cat_table = Ecomm_Category.objects.create(category_name="Table")
        
        self.p1 = Ecom_Product.objects.create(
            product_category=self.cat_sofa,
            product_name="Leather Sofa",
            product_description="Premium Italian leather sofa",
            product_price=30000.00,
            product_quantity_in_stock=5,
            product_is_featured=True
        )
        self.p2 = Ecom_Product.objects.create(
            product_category=self.cat_table,
            product_name="Oak Coffee Table",
            product_description="Solid oak wood table",
            product_price=4500.00,
            product_quantity_in_stock=0,
            product_is_featured=False
        )
        self.p3 = Ecom_Product.objects.create(
            product_category=self.cat_sofa,
            product_name="Fabric Armchair",
            product_description="Cozy fabric armchair",
            product_price=8000.00,
            product_quantity_in_stock=3,
            product_is_featured=False
        )

    def test_filter_by_category(self):
        res = self.client.get(reverse('products') + f'?category={self.cat_table.category_slug}')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Oak Coffee Table")
        self.assertNotContains(res, "Leather Sofa")

    def test_filter_by_price_preset(self):
        res = self.client.get(reverse('products') + '?price_range=under_5000')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Oak Coffee Table")
        self.assertNotContains(res, "Leather Sofa")

    def test_filter_by_custom_price(self):
        res = self.client.get(reverse('products') + '?min_price=5000&max_price=10000')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Fabric Armchair")
        self.assertNotContains(res, "Oak Coffee Table")
        self.assertNotContains(res, "Leather Sofa")

    def test_filter_by_in_stock(self):
        res = self.client.get(reverse('products') + '?in_stock=1')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Leather Sofa")
        self.assertContains(res, "Fabric Armchair")
        self.assertNotContains(res, "Oak Coffee Table")

    def test_filter_by_featured(self):
        res = self.client.get(reverse('products') + '?featured=1')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Leather Sofa")
        self.assertNotContains(res, "Fabric Armchair")

    def test_sorting_price_asc(self):
        res = self.client.get(reverse('products') + '?sort_by=price_asc')
        self.assertEqual(res.status_code, 200)
        prods = list(res.context['products'])
        self.assertEqual(prods[0].product_name, "Oak Coffee Table")
        self.assertEqual(prods[-1].product_name, "Leather Sofa")


