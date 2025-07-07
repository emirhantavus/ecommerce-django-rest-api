from rest_framework.test import APITestCase
from django.urls import reverse
from order.models import Order, OrderItem
from cart.models import CartItem
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class CancelOrderTest(APITestCase):
      def setUp(self):
            self.customer = User.objects.create_user(email="customer@gmail.com", password="passw0rd", role="customer")
            self.another_customer = User.objects.create_user(email="another@gmail.com", password="passw0rd", role="customer")
            self.seller = User.objects.create_user(email="seller@gmail.com", password="passw0rd", role="seller")
            self.product = Product.objects.create(name="product", price=100, stock=5, seller=self.seller)
            self.order = Order.objects.create(user=self.customer, address="adres", total_price=100, status='pending')
            self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=5, price=100)
            
            self.cancel_url = reverse('cancel-order', args=[self.order.id])
            
      def test_customer_can_cancel_pending_order(self):
            self.client.force_authenticate(user=self.customer)
            response=self.client.post(self.cancel_url)
            self.assertEqual(response.status_code, 200)
            self.order.refresh_from_db()
            self.assertEqual(self.order.status, 'cancelled')
            
      def test_customer_cannot_cancel_others_order(self):
            self.client.force_authenticate(user=self.another_customer)
            response = self.client.post(self.cancel_url)
            self.assertEqual(response.status_code, 404) # we get 404 bevause in views we control if order not found.
            # Because we control it with filter(id=o_id) for request.user, so we get 404 not 403.
            
      def test_customer_cannot_cancel_non_pending_order(self):
            #if order is 'shipped' or 'delivered', orders can not cancel.
            self.order.status = 'shipped'
            self.order.save()
            self.client.force_authenticate(user=self.customer)
            response = self.client.post(self.cancel_url)
            self.assertEqual(response.status_code, 400)
            
      def test_unauth_user_cannot_cancel_order(self):
            response = self.client.post(self.cancel_url)
            self.assertEqual(response.status_code, 401)
            
      def test_cancel_order_not_found(self):
            url = reverse('cancel-order', args=[421])
            self.client.force_authenticate(user=self.customer)
            response = self.client.post(url)
            self.assertEqual(response.status_code, 404)