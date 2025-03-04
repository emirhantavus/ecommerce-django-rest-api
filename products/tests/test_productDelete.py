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
            self.customer = User.objects.create_user(email="customer@gmail.com",password="passw0rd",role="customer")
            self.product = Product.objects.create(name="test product",price=100,stock=5,seller=self.seller)
            self.product_url = reverse('product-delete',kwargs={'pk':self.product.id})
            
      def test_delete_product_seller(self):
            self.client.force_authenticate(user=self.seller)
            response = self.client.delete(self.product_url)
            self.assertEqual(response.status_code, 204) # ok
            
      def test_delete_product_customer(self):
            self.client.force_authenticate(user=self.customer)
            response = self.client.delete(self.product_url)
            self.assertEqual(response.status_code, 403) # we should get 403 here.
            
      def test_delete_product_unauthenticated(self):
            response = self.client.delete(self.product_url)
            self.assertEqual(response.status_code, 401) # here we get 401 error.
            
      def test_delete_product_seller_with_login(self):
            data = {
                  'email':'seller@gmail.com',
                  'password':'passw0rd'
            }
            login_url = reverse('login')
            login_response = self.client.post(login_url, data)
            token = login_response.data['token']
            response = self.client.delete(self.product_url, HTTP_AUTHORIZATION=f"Token {token}")
            self.assertEqual(response.status_code, 204)
            
      def test_delete_product_customer_with_login(self):
            data = {
                  'email':'customer@gmail.com',
                  'password':'passw0rd'
            }
            login_url = reverse('login')
            login_response = self.client.post(login_url, data)
            token = login_response.data['token']
            response = self.client.delete(self.product_url, HTTP_AUTHORIZATION=f"Token {token}")
            self.assertEqual(response.status_code, 403)
            