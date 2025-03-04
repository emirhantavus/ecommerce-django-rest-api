from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import Product
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ProductListTestCase(APITestCase):
      def setUp(self):
            self.seller = User.objects.create_user(email="seller@gmail.com",password="passw0rd",role="seller")
            self.product_one = Product.objects.create(name="test product",price=100,stock=5,seller=self.seller)
            self.product_two = Product.objects.create(name="test product 2",price=10000,stock=10,seller=self.seller)
            self.product_all_url = reverse('products')
            self.product_pk_url = reverse('product-detail',kwargs={'pk':self.product_two.id})
            
      def test_get_all_products(self):
            response = self.client.get(self.product_all_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Product.objects.count(), 2)
            
      def test_get_pk_product(self):
            response = self.client.get(self.product_pk_url)
            self.assertEqual(response.status_code, 200)
            self.assertIn("name",response.data)
            self.assertIn('seller',response.data)
            self.assertIn('id',response.data['seller'])
            self.assertIn('email',response.data['seller'])
            self.assertIn('phone_number',response.data['seller'])
            