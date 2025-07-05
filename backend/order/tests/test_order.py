from rest_framework.test import APITestCase
from django.urls import reverse
from order.models import Order, OrderItem
from cart.models import CartItem
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class OrderTest(APITestCase):
      def setUp(self):
            self.seller = User.objects.create_user(email="seller@gmail.com",password="passw0rd",role="seller")
            self.customer = User.objects.create_user(email="customer@gmail.com",password="passw0rd",role="customer")
            self.product = Product.objects.create(name="test product",price=100,stock=5,seller=self.seller)
            self.cartItem = CartItem.objects.create(user=self.customer, product=self.product, quantity=3)
            self.order_url = reverse('order')
            
      def test_get_order_without_authenticate(self):
            response = self.client.get(self.order_url)
            self.assertEqual(response.status_code, 401) # ok
            
      def test_get_order_with_authenticate(self):
            self.client.force_authenticate(user=self.customer)
            response = self.client.get(self.order_url)
            self.assertEqual(response.status_code, 200) #ok
            self.assertEqual(len(response.data), 0)
            
      def test_make_order(self):
            self.client.force_authenticate(user=self.customer)
            data = {'address':'Test Address'}
            response = self.client.post(self.order_url, data)
            #we get total_price string here and convert to float.
            self.assertEqual(response.status_code, 201)
            self.assertEqual(float(response.data['total_price']),self.product.price * self.cartItem.quantity)
            
            ###test for get method with created data
            
            response = self.client.get(self.order_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Order.objects.count(), 1)
            self.assertEqual(OrderItem.objects.count(), 1)
            #self.assertEqual(response.data[0]['product_name'],self.product.name)
            #self.assertIn(self.product.name, [item['product_name'] for item in response.data[0]['items']])
            
            ####Look here, after creating paymnet models.. !!
            ####Need to make payment system to complete ORDER functionality
            ######## DONE in payment tests
            
      def test_cannot_create_order_when_cart_is_empty(self): 
            test_user = User.objects.create_user(email="test@gmail.com",password="passw0rd",role="customer")
            self.client.force_authenticate(user=test_user)
            data = {'address':'Test'}
            response = self.client.post(self.order_url, data)
            self.assertEqual(response.status_code, 400) # cart is empty so we get 400