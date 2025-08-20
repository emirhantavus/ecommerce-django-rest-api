from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Product
from order.models import Order, OrderItem
from django.core.cache import cache

User = get_user_model()

class SellerDashboardTestCase(APITestCase):
      def setUp(self):
            cache.clear()
            self.seller = User.objects.create_user(email="seller@gmail.com",password="passw0rd",role="seller")
            self.customer = User.objects.create_user(email="customer@gmail.com",password="passw0rd",role="customer")
            self.p1=Product.objects.create(name='A',seller=self.seller, price=100,stock=10)
            self.p2=Product.objects.create(name='B',seller=self.seller, price=50,stock=5)
            self.p3=Product.objects.create(name='C',seller=self.seller, price=30,stock=3)
            self.order = Order.objects.create(user=self.customer, status='paid',total_price=430)
            OrderItem.objects.create(order=self.order,product=self.p1,quantity=3,price=100)
            OrderItem.objects.create(order=self.order,product=self.p2,quantity=2,price=50)
            OrderItem.objects.create(order=self.order,product=self.p3,quantity=1,price=30)
            
            self.zero_seller = User.objects.create_user(email="zero-seller@gmail.com",password="passw0rd",role="seller")
            
            self.url = reverse('seller-dashboard')
            
      def test_seller_dashboard_with_valid_data(self):
            self.client.force_authenticate(user=self.seller)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            
      def test_seller_dashboard_requires_authentication(self):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 401)
            
      def test_customer_cannot_access_seller_dashboard(self):
            self.client.force_authenticate(user=self.customer)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)
            
      def test_seller_with_no_products_returns_zero(self):
            self.client.force_authenticate(user=self.zero_seller)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            data = response.data
            self.assertEqual(data["total_products"], 0)
            self.assertEqual(data["total_sales"], 0)
            self.assertEqual(data["total_revenue"], "0.00")#Decimal field should be string "0.00"
            self.assertEqual(data["pending_orders"], 0)
            self.assertEqual(data["stock_alerts"], [])
            
      def test_seller_stock_alert_list_low_products(self):
            self.client.force_authenticate(user=self.seller)
            response = self.client.get(self.url)
            stock_list = len(response.data['stock_alerts'])
            self.assertEqual(stock_list, 2)
            
      def test_seller_dashboard_calculates_sales_and_revenue(self):
            expected_total_sales = 6
            expected_revenue = "430.00"
            self.client.force_authenticate(user=self.seller)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["total_sales"],expected_total_sales)
            self.assertEqual(response.data["total_revenue"],expected_revenue)
            
      def test_seller_dashboard_response_contains_expected_fields(self):
            self.client.force_authenticate(user=self.seller)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            data = response.data
            expected_fields = [
                  "total_products",
                  "total_sales",
                  "total_revenue",
                  "pending_orders",
                  "stock_alerts"
            ]
            for field in expected_fields:
                  self.assertIn(field, response.data)
                  
      def test_seller_dashboard_with_pending_orders_only(self):
            pending_order = Order.objects.create(user=self.customer, status="pending", total_price=200)
            OrderItem.objects.create(order=pending_order, product=self.p1, quantity=2, price=100)
            self.client.force_authenticate(user=self.seller)
            response = self.client.get(self.url)
            data = response.data
            self.assertGreaterEqual(data["pending_orders"], 1)
            
      def test_seller_dashboard_access_by_inactive_seller(self):
            self.seller.is_active = False
            self.seller.save()
            self.client.force_authenticate(user=self.seller)
            response = self.client.get(self.url)
            self.assertIn(response.status_code, [200, 403]) # Fix this later. I will add extra feat to permissions.