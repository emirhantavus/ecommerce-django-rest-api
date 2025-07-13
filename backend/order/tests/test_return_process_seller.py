from rest_framework.test import APITestCase
from django.urls import reverse
from order.models import Order, OrderItem
from django.contrib.auth import get_user_model
from products.models import Product
from notifications.models import Notification

User = get_user_model()

class SellerReturnProcessTest(APITestCase):
      def setUp(self):
            self.seller = User.objects.create_user(email="seller@gmail.com", password="passw0rd", role="seller")
            self.other_seller = User.objects.create_user(email="otherseller@gmail.com", password="passw0rd", role="seller")
            self.customer = User.objects.create_user(email="customer@gmail.com", password="passw0rd", role="customer")

            self.product = Product.objects.create(name="test product", price=100, stock=5, seller=self.seller)
            self.other_product = Product.objects.create(name="other product", price=80, stock=7, seller=self.other_seller)

            self.order = Order.objects.create(user=self.customer, address="Test Adres", total_price=100, status='delivered')
            self.order_item = OrderItem.objects.create(
                order=self.order, product=self.product, quantity=1, price=100, return_status='requested', return_type='refund'
            )

            self.other_order_item = OrderItem.objects.create(
                order=self.order, product=self.other_product, quantity=1, price=80, return_status='requested', return_type='refund'
            )

            self.seller_return_list_url = reverse('seller-return-requests')
            self.process_return_url = reverse('process-return', args=[self.order_item.id])
            self.process_other_return_url = reverse('process-return', args=[self.other_order_item.id])
            
      def test_seller_can_list_own_product_return_requests(self):
            self.client.force_authenticate(user=self.seller)
            response = self.client.get(self.seller_return_list_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['id'], self.order_item.id)
            
      def test_seller_cannot_list_others_return_requests(self):
            self.client.force_authenticate(user=self.other_seller)
            response = self.client.get(self.seller_return_list_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['id'], self.other_order_item.id)
            
            ids = [item['id'] for item in response.data]
            self.assertNotIn(self.order_item.id, ids) #we check here if there is another process
            
      def test_seller_can_approve_return_request(self):
            self.client.force_authenticate(user=self.seller)
            data = {
                  'action':'approve'
            }
            response = self.client.post(self.process_return_url,data)
            self.assertEqual(response.status_code, 200)
            self.order_item.refresh_from_db()
            self.assertEqual(self.order_item.return_status, 'approved')
            
            notification = Notification.objects.filter(user=self.customer, subject__icontains="Approved").first()
            self.assertIsNotNone(notification)

      def test_seller_can_reject_return_request(self):
            self.client.force_authenticate(user=self.seller)
            data = {
                  'action':'reject'
            }
            response = self.client.post(self.process_return_url,data)
            self.assertEqual(response.status_code, 200)
            self.order_item.refresh_from_db()
            self.assertEqual(self.order_item.return_status, 'rejected')
            
            notification = Notification.objects.filter(user=self.customer, subject__icontains="Rejected").first()
            self.assertIsNotNone(notification)

      def test_seller_cannot_process_another_sellers_request(self):
            self.client.force_authenticate(user=self.other_seller)
            data = {
                  'action':'approve' # or 'reject' doesn't matter
            }
            response = self.client.post(self.process_return_url,data)
            self.assertEqual(response.status_code, 404)

      def test_seller_cannot_process_non_requested_status(self):
            order_item_none = OrderItem.objects.create(
                  order=self.order,
                  product=self.product,
                  quantity=1,
                  price=100,
                  return_status='none',
                  return_type='refund'
            )
            process_url = reverse('process-return', args=[order_item_none.id])
            
            self.client.force_authenticate(user=self.seller)
            data = {
                  'action':'approve'
            }
            response = self.client.post(process_url,data)
            self.assertEqual(response.status_code, 404)

      def test_unauthorized_user_cannot_process_return_request(self):
            data = {
                  'action':'reject'
            }
            response = self.client.post(self.process_return_url,data)
            self.assertEqual(response.status_code, 401)

      def test_cannot_process_return_with_invalid_action(self):
            self.client.force_authenticate(user=self.seller)
            data = {
                  'action':'INVALID_ACTION'
            }
            response = self.client.post(self.process_return_url,data)
            self.assertEqual(response.status_code, 400)

      def test_return_request_not_found_returns_404(self):
            self.client.force_authenticate(user=self.seller)
            invalid_id_url = reverse('process-return', args=[1232313])
            data = {
                  'action':'approve'
            }
            response = self.client.post(invalid_id_url,data)
            self.assertEqual(response.status_code, 404)