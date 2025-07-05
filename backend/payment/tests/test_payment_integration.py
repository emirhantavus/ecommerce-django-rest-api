from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from order.models import Order
from products.models import Product
from cart.models import CartItem

User = get_user_model()

class PaymentIntegrationTestCase(APITestCase):
      def setUp(self):
            self.user = User.objects.create_user(email='user@gmail.com',password='passw0rd')
            self.seller = User.objects.create_user(email='seller@gmail.com',password='passw0rd')
            self.product = Product.objects.create(name='Guitar',price=300, stock=99, seller=self.seller)
            
            self.cart_data = {
                  'product':self.product.id,
                  'quantity':3
            }
            
            self.cart_url = reverse('cart-list-create')
            self.order_url = reverse('order')
            self.payment_url = reverse('payment')
            
      def test_payment_integration_success(self):
            self.client.force_authenticate(user=self.user)
            response = self.client.post(self.cart_url,self.cart_data) # POST cart
            self.assertEqual(response.status_code, 201)
            
            response = self.client.get(self.cart_url)
            self.assertEqual(response.status_code, 200) # GET cart
            self.assertEqual(len(response.data['items']), 1)
            
            
            order_data = {
                  'address':'test address'
            }
            response = self.client.post(self.order_url, order_data)
            self.assertEqual(response.status_code, 201) #POST order
            self.assertEqual(response.data['status'],'pending')
            order_id = response.data['id']
            
            response = self.client.get(self.order_url)
            self.assertEqual(response.status_code, 200) # empty for now cuz we show only 'paid' orders.
            
            payment_data = {
                  'order':order_id
            }
            
            response = self.client.post(self.payment_url, payment_data)
            self.assertEqual(response.status_code, 201) # POST payment
            
            payment_status = response.data['status']
            
            response = self.client.get(self.order_url)
            self.assertEqual(response.status_code, 200) #GET order status 'paid'
            
            order_status = response.data[0]['status']
            
            if payment_status: # We check here if payment status is True, then Order status is 'paid'
                  self.assertEqual(order_status, 'paid')
                  self.assertEqual(len(response.data), 1)
            else:
                  self.assertEqual(order_status, 'failed')
                  self.assertEqual(len(response.data), 0)