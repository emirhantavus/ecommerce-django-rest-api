from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from order.models import Order
from products.models import Product
from cart.models import CartItem
from notifications.models import Notification

User=get_user_model()

class PaymentNotificationTestCase(APITestCase):
      def setUp(self):
            self.customer = User.objects.create_user(email="customer@gmail.com", password="passw0rd", role="customer")
            self.seller = User.objects.create_user(email="seller@gmail.com", password="passw0rd", role="seller")
            self.product = Product.objects.create(name="Laptop", price=150, stock=10, seller=self.seller)
            self.cart_item = CartItem.objects.create(user=self.customer, product=self.product, quantity=2)
            self.order_url = reverse('order')
            self.payment_url = reverse('payment')

      def test_payment_creates_notifications(self):
            self.client.force_authenticate(user=self.customer)

            order = Order.objects.create(
                  user=self.customer,
                  address='Github',
                  total_price=self.cart_item.quantity * self.cart_item.product.price
            )

            data = {'order': order.id}
            response = self.client.post(self.payment_url, data)
            self.assertEqual(response.status_code, 201)

            if response.data['status'] is True or response.data['status'] == True:
                  #If True, We sent notification for both of them.
                  notif_customer = Notification.objects.filter(user=self.customer, subject__icontains="Order Has Been Recieved").first()
                  self.assertIsNotNone(notif_customer)

                  notif_seller = Notification.objects.filter(user=self.seller, subject__icontains="New Order Received").first()
                  self.assertIsNotNone(notif_seller)
            else: #If False, then we just send for customer for failed payment.
                  notif_fail = Notification.objects.filter(user=self.customer, subject__icontains="Failed").first()
                  self.assertIsNotNone(notif_fail)
