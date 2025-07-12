from rest_framework.test import APITestCase
from django.urls import reverse
from order.models import Order, OrderItem
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class CustomerReturnRequestTest(APITestCase):
      def setUp(self):
            self.seller = User.objects.create_user(email="seller@gmail.com", password="passw0rd", role="seller")
            self.customer = User.objects.create_user(email="customer@gmail.com", password="passw0rd", role="customer")
            self.other_customer = User.objects.create_user(email="othercustomer@gmail.com", password="passw0rd", role="customer")
            
            self.product = Product.objects.create(name="test product", price=100, stock=5, seller=self.seller)
            self.order = Order.objects.create(user=self.customer, address="Test Adres", total_price=100, status='delivered')
            self.undelivered_order = Order.objects.create(user=self.other_customer, address="Test Adres", total_price=100, status='shipped')
            
            self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price=100)
            self.undelivered_order_item = OrderItem.objects.create(order=self.undelivered_order, product=self.product, quantity=1, price=100)
            
            self.return_url = reverse('request-return', args=[self.order_item.id])
            self.ud_return_url = reverse('request-return', args=[self.undelivered_order_item.id])
            self.list_return_url = reverse('my-return-requests')
            
      def test_customer_can_request_return_delivered_item(self):
            self.client.force_authenticate(user=self.customer)
            data = {
                  "return_type": "refund",
                  "return_reason": "Product_X was broken"
            }
            response = self.client.post(self.return_url, data)
            self.assertEqual(response.status_code, 200)
            self.order_item.refresh_from_db()
            self.assertEqual(self.order_item.return_status, 'requested')
            
      def test_customer_cannot_request_return_undelivered_item(self):
            self.client.force_authenticate(user=self.other_customer)
            data = {
                  "return_type": "refund",
                  "return_reason": "Product_X was broken"
            }
            response = self.client.post(self.ud_return_url, data)
            self.assertEqual(response.status_code, 400)
            
      def test_customer_cannot_request_return_twice(self):
            self.client.force_authenticate(user=self.customer)
            data = {
                  "return_type": "refund",
                  "return_reason": "Product_X was broken"
            }
            response = self.client.post(self.return_url, data)
            self.assertEqual(response.status_code, 200)
            self.order_item.refresh_from_db()
            self.assertEqual(self.order_item.return_status, 'requested')
            
            ## twice
            
            response = self.client.post(self.return_url, data)
            self.assertEqual(response.status_code, 400) # we get 400 here for twice request.
            
      def test_customer_cannot_request_return_on_another_users_item(self):
            '''
            order=self.customer -- request=self.other_customer
            So we get 404 here.
            '''
            self.client.force_authenticate(user=self.other_customer)
            data = {
                  "return_type": "refund",
                  "return_reason": "Product_X was broken"
            }
            response = self.client.post(self.return_url, data)
            self.assertEqual(response.status_code, 404)
            
      def test_unauthorized_user_cannot_request_return(self):
            data = {
                  "return_type": "refund",
                  "return_reason": "Product_X was broken"
            }
            response = self.client.post(self.return_url, data)
            self.assertEqual(response.status_code, 401)
            
      def test_customer_can_list_own_return_requests(self):
            # we add first. then list them.
            self.client.force_authenticate(user=self.customer)
            data = {
                  "return_type": "refund",
                  "return_reason": "Product_X was broken"
            }
            response = self.client.post(self.return_url, data)
            self.assertEqual(response.status_code, 200)
            self.order_item.refresh_from_db()
            self.assertEqual(self.order_item.return_status, 'requested')
            
            ## list here
            
            response = self.client.get(self.list_return_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['id'], self.order_item.id)