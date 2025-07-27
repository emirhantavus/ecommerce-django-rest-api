from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product
from order.models import Order, OrderItem
from ..models import Review

User = get_user_model()

class ReviewTests(APITestCase):
      def setUp(self):
            self.seller = User.objects.create_user(email='seller@gmail.com', password='passw0rd', role='seller')
            self.customer = User.objects.create_user(email='customer@gmail.com', password='passw0rd', role='customer')
            self.customer2 = User.objects.create_user(email='customer2@gmail.com', password='passw0rd', role='customer')

            self.product = Product.objects.create(name='Test Product', seller=self.seller, price=100, stock=10)

            self.order = Order.objects.create(user=self.customer, status='delivered', total_price=100)
            self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price=100)

            self.create_url = reverse('review-create', kwargs={'product_id': self.product.id})
            self.update_url = lambda review_id: reverse('review-detail', kwargs={'pk': review_id})
            self.product_reviews_url = reverse('product-reviews', kwargs={'product_id': self.product.id})
            self.user_reviews_url = reverse('user-reviews')
            
      def test_create_review_authenticated(self):
            pass
      def test_create_review_unauthenticated(self):
            pass
      def test_create_review_not_purchased(self):
            pass
      def test_update_review_owner(self):
            pass
      def test_update_review_not_owner(self):
            pass
      def test_delete_review_owner(self):
            pass
      def test_delete_review_not_owner(self):
            pass
      def test_get_product_reviews(self):
            pass
      def test_get_user_reviews(self):
            pass
      def test_duplicate_review_blocked(self):
            pass
      def test_rating_average_and_count(self):
            pass
      def test_review_with_invalid_rating(self):
            pass
      def test_review_with_empty_comment(self):
            pass
      def test_review_edit_after_delete(self):
            pass
      def test_review_response_fields(self):
            pass