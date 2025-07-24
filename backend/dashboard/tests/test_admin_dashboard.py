from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product
from order.models import Order, OrderItem

User = get_user_model()

class AdminDashboardTests(APITestCase):
      def setUp(self):
            self.admin_user = User.objects.create_user(email='admin@gmail.com', password='passw0rd', role='admin')
            self.seller_user = User.objects.create_user(email='seller@gmail.com', password='passw0rd', role='seller')
            self.customer_user = User.objects.create_user(email='customer@gmail.com', password='passw0rd', role='customer')
            self.url = reverse('admin-dashboard')

      def create_extra_users(self):
            User.objects.create_user(email='seller1@gmail.com', password='passw0rd', role='seller')
            User.objects.create_user(email='seller2@gmail.com', password='passw0rd', role='seller')
            User.objects.create_user(email='customer1@gmail.com', password='passw0rd', role='customer')
            User.objects.create_user(email='customer2@gmail.com', password='passw0rd', role='customer')

      def create_products_and_order(self):
            self.create_extra_users()
            seller1 = User.objects.get(email='seller1@gmail.com')
            seller2 = User.objects.get(email='seller2@gmail.com')
            customer = User.objects.get(email='customer1@gmail.com')

            p1 = Product.objects.create(name='p1', seller=seller1, price=100, stock=40)
            p2 = Product.objects.create(name='p2', seller=seller2, price=55, stock=22)

            order = Order.objects.create(user=customer, address='deneme', total_price=0)
            OrderItem.objects.create(order=order, product=p1, quantity=2, price=100) # 200
            OrderItem.objects.create(order=order, product=p2, quantity=1, price=55) # 55
            order.total_price = 255
            order.save()

      def test_admin_can_access_dashboard(self):
            self.client.force_authenticate(user=self.admin_user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

      def test_seller_cannot_access_admin_dashboard(self):
            self.client.force_authenticate(user=self.seller_user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)

      def test_customer_cannot_access_admin_dashboard(self):
            self.client.force_authenticate(user=self.customer_user)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)

      def test_anonymous_user_cannot_access_admin_dashboard(self):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 401)

      def test_admin_dashboard_returns_correct_data(self):
            self.create_products_and_order()
            self.client.force_authenticate(user=self.admin_user)
            response = self.client.get(self.url)
            data = response.json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['total_users'], 7)  # 3 setup + 3 create_extra_users #including admin for now +1
            self.assertEqual(data['total_sellers'], 3)  # 1 setup + 2 extra
            self.assertEqual(data['total_products'], 2)
            self.assertEqual(data['total_orders'], 1)
            self.assertEqual(data['total_revenue'], '255.00')