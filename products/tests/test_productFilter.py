from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import Product , Category
from django.urls import reverse

User = get_user_model()

class ProductFilterTestCase(APITestCase):
      def setUp(self):
            self.category = Category.objects.create(name="cat")
            self.seller = User.objects.create_user(email="seller@gmail.com",password="passw0rd",role="seller")
            self.product_one = Product.objects.create(name="test product 1",price=100,stock=5,seller=self.seller,category=self.category)
            self.product_two = Product.objects.create(name="test product 2",price=50,stock=10,seller=self.seller)
            self.product_three = Product.objects.create(name="test product 3",price=20,stock=20,seller=self.seller)
            self.product_four = Product.objects.create(name="test product 4",price=400,stock=50,seller=self.seller,discount=True,discount_rate=50)
            self.product_five = Product.objects.create(name="test product 5",price=2,stock=2,seller=self.seller)
            self.product_six = Product.objects.create(name="test product 5",price=30,stock=0,seller=self.seller)
            self.product_seven = Product.objects.create(name="deneme",price=70,stock=0,seller=self.seller)
            self.product_url = reverse('products')
            
      def test_filter_by_seller(self):
            response = self.client.get(self.product_url, {'seller':self.seller.id})
            self.assertEqual(response.status_code, 200)
            for product in response.data['results']:
                  self.assertEqual(product['seller']['id'], self.seller.id)
            
      def test_filter_by_category(self):
            response = self.client.get(self.product_url, {'category':self.product_one.category.name})
            self.assertEqual(response.status_code, 200)
            
      def test_filter_by_price(self):
            response = self.client.get(self.product_url, {'max_price':200,'min_price':50})
            self.assertEqual(response.status_code, 200)
            for product in response.data['results']:
                  self.assertGreaterEqual(product['price'],50)
                  self.assertLessEqual(product['price'], 200)
            self.assertEqual(len(response.data['results']), 3)
            
      def test_filter_by_in_stock(self):
            response = self.client.get(self.product_url, {'stock':1}) # 1 means True here.
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data['results']), 5)
            
      def test_filter_by_not_in_stock(self):
            response = self.client.get(self.product_url, {'stock':0}) # 0 means False here.
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data['results']), 2)
            
      def test_filter_by_discounted(self):
            response = self.client.get(self.product_url, {'discount':'true'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data['results']), 1)
            response = self.client.get(self.product_url, {'discount':'false'})
            self.assertEqual(len(response.data['results']), 6)
            
      def test_product_search(self):
            response = self.client.get(self.product_url, {'search':'deneme'})
            self.assertEqual(response.status_code, 200)
            self.assertGreaterEqual(len(response.data['results']), 0)
            self.assertEqual(len(response.data['results']),1)
            self.assertEqual(response.data['results'][0]['name'], 'deneme')
            
      def test_sort_by_created_at(self):
            response = self.client.get(self.product_url, {'sort_by':'created_at'})#default order:'asc'
            self.assertEqual(response.status_code, 200)
            response_order = self.client.get(self.product_url, {'sort_by':'created_at','order':'desc'})
            self.assertEqual(response_order.status_code, 200)
            
      def test_sort_by_created_at(self):
            response = self.client.get(self.product_url, {'sort_by':'price'})
            self.assertEqual(response.status_code, 200)
            response_order = self.client.get(self.product_url, {'sort_by':'price','order':'desc'})
            self.assertEqual(response_order.status_code, 200)
            
      def test_sort_by_stock(self):
            response = self.client.get(self.product_url, {'sort_by':'stock'})
            self.assertEqual(response.status_code, 200)
            response_order = self.client.get(self.product_url, {'sort_by':'stock','order':'desc'})
            self.assertEqual(response_order.status_code, 200)