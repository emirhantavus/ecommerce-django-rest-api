from unittest.mock import patch
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product
from order.models import Order, OrderItem

User = get_user_model()

class ShipOrderItemAPITest(APITestCase):
      def setUp(self):
            self.seller = User.objects.create_user(email="seller@gmail.com", password="passw0rd", role="seller")
            self.other = User.objects.create_user(email="other@gmail.com", password="passw0rd", role="seller")
            self.customer = User.objects.create_user(email="customer@gmail.com", password="passw0rd", role="customer")
            self.product = Product.objects.create(name="Laptop", price=240, stock=5, seller=self.seller)
            self.order = Order.objects.create(user=self.customer, address="TR", total_price=240, status="paid")
            self.item = OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price=240)
            
            self.url = reverse('order-item-ship',args=[self.item.id])
      
      @patch('order.views.send_notification_and_email')
      @patch("order.views.create_shipment")
      def test_seller_can_ship_own_item(self, mock_ship, mock_notify):
            mock_ship.return_value = {
                  "id": "uid1",
                  "tracking_number":"T-deneme123",
                  "status":"pending"
            }
            
            self.client.force_authenticate(self.seller)
            response = self.client.post(self.url)
            
            self.assertEqual(response.status_code, 201)
            self.item.refresh_from_db()
            
            mock_ship.assert_called_once()
            mock_notify.assert_called_once()
            _, kwargs = mock_notify.call_args
            self.assertIn("Shipped", kwargs["subject"])
            
      def test_unauth_cannot_ship(self):
            response = self.client.post(self.url)
            self.assertEqual(response.status_code, 401)
            
      def test_seller_cannot_ship_others_item(self):
            self.client.force_authenticate(self.other)
            response = self.client.post(self.url)
            self.assertEqual(response.status_code,403)
            
      @patch("order.views.create_shipment")
      def test_cannot_ship_twice(self, _mock_ship):
            self.item.tracking_number = 'T-dd'
            self.item.save()
            
            self.client.force_authenticate(self.seller)
            response = self.client.post(self.url)
            self.assertEqual(response.status_code,400)
            
      @patch("order.views.create_shipment")
      @patch("order.views.send_notification_and_email")
      def test_shipment_service_error_returns_500(self, mock_notify, mock_ship):
            mock_ship.return_value = {'error':'Service Down !!'}
            
            self.client.force_authenticate(self.seller)
            response = self.client.post(self.url)
            
            self.assertEqual(response.status_code, 500)
            mock_notify.assert_not_called()