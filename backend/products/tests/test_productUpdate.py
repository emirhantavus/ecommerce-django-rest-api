from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product
from django.urls import reverse

User = get_user_model()

class ProductUpdateTestCase(APITestCase):
      def setUp(self):
            self.seller = User.objects.create_user(
                  email="seller@gmail.com", 
                  password="passw0rd", 
                  role="seller")
            
            self.customer = User.objects.create_user(
                  email="customer@gmail.com", 
                  password="passw0rd", 
                  role="customer")

            self.product = Product.objects.create(name="Test Product", seller=self.seller, price=100, stock=10)

            self.update_url = reverse('product-update',kwargs={'pk':self.product.id})

      def test_seller_can_update_product_put(self):
            self.client.force_authenticate(user=self.seller)
            response = self.client.put(self.update_url, {"name": "Updated Product PUT","price":100,"stock":5})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.product.refresh_from_db()
            self.assertEqual(self.product.name, "Updated Product PUT")
      
      def test_seller_can_update_product_patch(self):
            self.client.force_authenticate(user=self.seller)
            response = self.client.patch(self.update_url, {"name": "Updated Product PATCH"})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.product.refresh_from_db()
            self.assertEqual(self.product.name, "Updated Product PATCH")

      def test_customer_cannot_update_product(self):
            self.client.force_authenticate(user=self.customer)
            response = self.client.put(self.update_url, {"name": "Updated Product", "price": 200})
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
