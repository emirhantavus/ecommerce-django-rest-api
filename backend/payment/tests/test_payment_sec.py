from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from order.models import Order
from products.models import Product
from cart.models import CartItem

User = get_user_model()

class TestPaymentSecurity(APITestCase):
      def setUp(self):
            self.customer = User.objects.create_user(email="customer@gmail.com", password="passw0rd", role="customer")
            self.hacker = User.objects.create_user(email='hacker@gmail.com',password='passw0rd', role='customer')
            self.seller = User.objects.create_user(email="seller@gmail.com", password="passw0rd", role="seller")

            self.product = Product.objects.create(name="Laptop", price=150, stock=10, seller=self.seller)
            self.cart_item = CartItem.objects.create(user=self.hacker, product=self.product, quantity=2)

            self.order_url = reverse('order')
            self.payment_url = reverse('payment')
            
      def test_payment_with_forbidden(self):
            self.client.force_authenticate(user=self.customer)
            
            order = Order.objects.create(
                  user=self.hacker,
                  address='sec',
                  total_price=self.cart_item.quantity * self.cart_item.product.price
            )
            
            data = {
                  'order':order.id
            }
            
            response = self.client.post(self.payment_url, data)
            self.assertEqual(response.status_code, 403) # fixed it in serializer
            
      def test_duplicate_transaction_id_fail(self):
            self.client.force_authenticate(user=self.customer)
            
            order = Order.objects.create(
                  user=self.customer,
                  address='sec',
                  total_price=self.cart_item.quantity * self.cart_item.product.price
            )
            
            data = {
                  'order':order.id
            }
            
            response = self.client.post(self.payment_url, data)
            self.assertEqual(response.status_code, 201)
            transaction_id = response.data['transaction_id']
            
            fail_data = {
                  'order':order.id,
                  'transaction_id': transaction_id
            }
            
            fail_response = self.client.post(self.payment_url, fail_data)
            self.assertEqual(fail_response.status_code, 400) # we got 400 here