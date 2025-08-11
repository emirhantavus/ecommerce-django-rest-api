from unittest.mock import patch
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product
from order.models import Order, OrderItem

User = get_user_model()

class ShipmentWebhookAPITest(APITestCase):
      def setUp(self):
            self.seller = User.objects.create_user(email="seller@gmail.com", password="passw0rd", role="seller")
            self.customer = User.objects.create_user(email="customer@gmail.com", password="passw0rd", role="customer")
            self.product = Product.objects.create(name="Laptop", price=240, stock=5, seller=self.seller)
            self.order = Order.objects.create(user=self.customer, address="TR", total_price=240, status="paid")
            self.item = OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price=240, tracking_number="T-abc123")
            self.url = reverse("shipment-status-webhook")
            
            
      @patch('order.views.send_notification_and_email')
      def test_delivered_email(self, mock_notify):
            payload = {'tracking_number':self.item.tracking_number,'status':'delivered'}
            response = self.client.post(self.url, data=payload, format='json')
            self.assertEqual(response.status_code,200)
            mock_notify.assert_called_once()
            _, kwargs = mock_notify.call_args
            self.assertEqual(kwargs['user'], self.order.user)
            self.assertIn('Delivered', kwargs['subject'])
            
      @patch('order.views.send_notification_and_email')
      def test_in_transit_email(self, mock_notify):
            payload = {'tracking_number':self.item.tracking_number,'status':'in_transit'}
            response = self.client.post(self.url, data=payload, format='json')
            self.assertEqual(response.status_code, 200)
            mock_notify.assert_not_called()