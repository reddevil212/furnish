from django.db import models
from django.utils.text import slugify

# Create your models here.
class Ecomm_Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    category_slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    category_desc = models.TextField(blank=True, null=True)
    category_image = models.ImageField(upload_to="categories/", blank=True, null=True)
    category_created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.category_slug and self.category_name:
            self.category_slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name


class Ecom_Product(models.Model):
    product_category = models.ForeignKey(Ecomm_Category, on_delete=models.CASCADE, related_name="products")
    product_name = models.CharField(max_length=150, unique=True)
    product_slug = models.SlugField(max_length=150, unique=True)
    product_image = models.ImageField(upload_to="products/", null=True, blank=True)
    product_description = models.TextField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_quantity_in_stock = models.IntegerField()
    product_is_active = models.BooleanField(default=True)
    product_is_featured = models.BooleanField(default=False)
    product_created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.product_slug and self.product_name:
            self.product_slug = slugify(self.product_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name


