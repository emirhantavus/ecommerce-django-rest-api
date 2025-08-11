from rest_framework.test import APITestCase
from django.urls import reverse
from order.models import Order, OrderItem
from cart.models import CartItem
from django.contrib.auth import get_user_model
from products.models import Product
from notifications.models import Notification
from unittest import skip

User = get_user_model()

class OrderStatusTest(APITestCase):
      def setUp(self):
            self.seller = User.objects.create_user(email="seller@gmail.com", password="passw0rd", role="seller")
            self.diff_seller = User.objects.create_user(email="diffseller@gmail.com", password="passw0rd", role="seller")
            self.admin = User.objects.create_user(email='admin@gmail.com',password='passw0rd',role='admin')
            self.customer = User.objects.create_user(email="customer@gmail.com", password="passw0rd", role="customer")
            self.product = Product.objects.create(name="test product", price=100, stock=5, seller=self.seller)
            self.cart_item = CartItem.objects.create(user=self.customer, product=self.product, quantity=3)
            self.order = Order.objects.create(user=self.customer, address="Test adres", total_price=300, status='pending')
            self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=3, price=100)
            
            self.update_status_url = reverse('update-order-status', args=[self.order.id])
      
      @skip("No need because of fastapi microservise")
      def test_seller_can_update_own_order_status(self):
            self.client.force_authenticate(user=self.seller)
            data = {'status':'shipped'}
            response = self.client.patch(self.update_status_url, data)
            self.assertEqual(response.status_code, 200)
            self.order.refresh_from_db()
            self.assertEqual(self.order.status, 'shipped')
            
            notification = Notification.objects.filter(user=self.customer, subject__icontains="shipped").first()
            self.assertIsNotNone(notification)
      
      @skip("!")
      def test_seller_cannot_update_other_seller_status(self):
            self.client.force_authenticate(user=self.diff_seller)
            data = {'status':'shipped'}
            response = self.client.patch(self.update_status_url, data)
            self.assertEqual(response.status_code, 403) # forbidden
      
      @skip("!")
      def test_admin_can_update_any_order_status(self):
            self.client.force_authenticate(user=self.admin)
            data = {'status':'shipped'}
            response = self.client.patch(self.update_status_url, data)
            self.assertEqual(response.status_code, 200)
            self.order.refresh_from_db()
            self.assertEqual(self.order.status, 'shipped')
            '''
                  It works actually but probably we will not create 'admin' role for user model. Better to create it in
                  superuser model
            '''
            
      @skip("!")
      def test_invalid_status_rejected(self):
            self.client.force_authenticate(user=self.seller)
            data = {'status':'invalid_status'}
            response = self.client.patch(self.update_status_url, data)
            self.assertEqual(response.status_code, 400)
            
      @skip("!")
      def test_order_not_found(self):
            update_status_not_found_url = reverse('update-order-status', args=[1111])
            self.client.force_authenticate(user=self.seller)
            data = {'status':'shipped'}
            response = self.client.patch(update_status_not_found_url, data)
            self.assertEqual(response.status_code, 404)
      
      @skip("!")
      def test_unauth_user_cannot_update_order(self):
            data = {'status':'shipped'}
            response = self.client.patch(self.update_status_url, data)
            self.assertEqual(response.status_code, 401)
      
      @skip("!")
      def test_update_order_status_cancelled(self):
            old_stock = self.product.stock
            self.client.force_authenticate(user=self.seller)
            data = {'status':'cancelled'}
            response = self.client.patch(self.update_status_url, data)
            self.assertEqual(response.status_code, 200)
            self.product.refresh_from_db()
            self.assertEqual(self.product.stock, old_stock + self.order_item.quantity)
            
            notification = Notification.objects.filter(user=self.customer, subject__icontains="cancelled").first()
            self.assertIsNotNone(notification)