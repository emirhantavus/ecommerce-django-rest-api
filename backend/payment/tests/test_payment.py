from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from order.models import Order
from products.models import Product
from cart.models import CartItem

User = get_user_model()

class PaymentTestCase(APITestCase):
      def setUp(self):
            self.customer = User.objects.create_user(email="customer@gmail.com", password="passw0rd", role="customer")
            self.seller = User.objects.create_user(email="seller@gmail.com", password="passw0rd", role="seller")

            self.product = Product.objects.create(name="Laptop", price=150, stock=10, seller=self.seller)
            self.cart_item = CartItem.objects.create(user=self.customer, product=self.product, quantity=2)

            self.order_url = reverse('order')
            self.payment_url = reverse('payment')
            
      def test_payment_without_auth(self):
            data = {}
            response = self.client.post(self.payment_url, data)
            self.assertEqual(response.status_code, 401) #OK
            
      def test_successful_payment(self):
            self.client.force_authenticate(user=self.customer)
            
            order = Order.objects.create(
                  user=self.customer,
                  address='Github',
                  total_price=self.cart_item.quantity * self.cart_item.product.price
            )
            
            data = {
                  'order':order.id
            }
            response = self.client.post(self.payment_url, data)
            self.assertEqual(response.status_code, 201)
            self.assertIn('transaction_id', response.data)
            self.assertIn('status',response.data)
            
      def test_invalid_id_payment(self):
            self.client.force_authenticate(user=self.customer)
            data = {'order':41239}
            response = self.client.post(self.payment_url, data)
            self.assertEqual(response.status_code, 400)
            
      def test_double_payment_should_fail(self):
            self.client.force_authenticate(user=self.customer)
            
            order = Order.objects.create(
                  user=self.customer,
                  address='Github',
                  total_price=self.cart_item.quantity * self.cart_item.product.price
            )
            
            data = {
                  'order':order.id
            }
            response = self.client.post(self.payment_url, data)
            self.assertEqual(response.status_code, 201)
            response = self.client.post(self.payment_url, data)
            self.assertEqual(response.status_code, 400)
            
      def test_order_status_updated_after_successful_payment(self):
            self.client.force_authenticate(user=self.customer)
            order = Order.objects.create(
                  user=self.customer,
                  address='Git',
                  total_price = self.cart_item.product.price * self.cart_item.quantity
            )
            data = {'order': order.id}
            response = self.client.post(self.payment_url, data)
            order.refresh_from_db()
            if response.data['status'] is True or response.data['status'] == True:
                  self.assertEqual(order.status, 'paid')
            else:
                  self.assertEqual(order.status, 'failed')  #It works.
            
      def test_list_payments_no_auth(self):
            response = self.client.get(self.payment_url)
            self.assertEqual(response.status_code, 401)
            
      def test_list_payments_success(self):
            self.client.force_authenticate(user=self.customer)
            response = self.client.get(self.payment_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data),0)
            ## it works but I want to make a payment
            order = Order.objects.create(
                  user=self.customer,
                  address='Git',
                  total_price = self.cart_item.product.price * self.cart_item.quantity
            )
            data = {'order': order.id}
            response = self.client.post(self.payment_url, data)
            self.assertEqual(response.status_code, 201)
            
            response = self.client.get(self.payment_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 1)
