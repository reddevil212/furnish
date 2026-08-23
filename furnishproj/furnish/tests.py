from django.test import TestCase, Client
from django.urls import reverse
from .models import Ecomm_Category, Ecom_Product

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

