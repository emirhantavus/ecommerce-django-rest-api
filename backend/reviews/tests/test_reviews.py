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

            self.create_url = reverse('product-review', kwargs={'product_id': self.product.id})
            self.user_reviews_url = reverse('my-reviews')
            
      def test_create_review_authenticated(self):
            self.client.force_authenticate(user=self.customer)
            data = {
                  "rating":5,
                  "comment":"test"
            }
            response = self.client.post(self.create_url,data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['rating'], 5)
            self.assertEqual(response.data['comment'], "test")
            self.assertEqual(response.data['user']['id'], self.customer.id)
            self.assertEqual(response.data['product']['id'],self.product.id)
            self.assertIn("created_at", response.data)
            
            self.assertTrue(Review.objects.filter(user=self.customer,product=self.product,rating=5,comment="test").exists())
            self.assertIsInstance(response.data, dict)
            
      def test_create_review_unauthenticated(self):
            data = {
                  "rating":5,
                  "comment":"test"
            }
            response = self.client.post(self.create_url,data)
            self.assertEqual(response.status_code,401)
            
      def test_create_review_not_purchased(self):
            self.client.force_authenticate(user=self.customer2)
            data = {
                  "rating":5,
                  "comment":"test"
            }
            response = self.client.post(self.create_url, data)
            self.assertEqual(response.status_code, 403)
            
      def test_update_review_owner(self):
            self.client.force_authenticate(user=self.customer)
            data = {
                  "rating":5,
                  "comment":"test"
            }
            response = self.client.post(self.create_url,data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['rating'], 5)
            self.assertEqual(response.data['comment'], "test")
            
            r_id = response.data['id']
            ## now update
            
            update_url = reverse('review-detail', kwargs={'pk':r_id})
            new_data = {
                  "rating":1,
                  "comment":"updated test"
            }
            response = self.client.patch(update_url, new_data)
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.data['rating'],1) #updated rating
            self.assertEqual(response.data['comment'],'updated test')
            
      def test_update_review_not_owner(self):
            self.client.force_authenticate(user=self.customer)
            data = {
                  "rating":5,
                  "comment":"test"
            }
            response = self.client.post(self.create_url,data)
            self.assertEqual(response.status_code, 201)
            r_id = response.data['id']
            
            self.client.logout()
            self.client.force_authenticate(user=self.customer2)
            new_data = {
                  "rating":1,
                  "comment":"updated test"
            }
            update_url = reverse('review-detail', kwargs={'pk':r_id})
            response = self.client.patch(update_url, new_data)
            self.assertEqual(response.status_code,404)
            # used get_object_or_404 that's why I get 404 status code
            #maybe I change it later idk what is clean code for this ex.

      def test_delete_review_owner(self):
            self.client.force_authenticate(user=self.customer)
            data = {
                  "rating":5,
                  "comment":"test"
            }
            response = self.client.post(self.create_url,data)
            self.assertEqual(response.status_code, 201)
            r_id = response.data['id']
            
            ## delete here
            delete_url = reverse('review-detail', kwargs={'pk':r_id})
            response = self.client.delete(delete_url)
            self.assertEqual(response.status_code, 204)
            self.assertEqual(response.data['message'], 'Review deleted.!')
      def test_delete_review_not_owner(self):
            self.client.force_authenticate(user=self.customer)
            data = {
                  "rating":5,
                  "comment":"test"
            }
            response = self.client.post(self.create_url,data)
            self.assertEqual(response.status_code, 201)
            r_id = response.data['id']
            
            ## try to delete but no way.
            self.client.logout()
            self.client.force_authenticate(user=self.customer2)
            delete_url = reverse('review-detail', kwargs={'pk':r_id})
            response = self.client.delete(delete_url)
            self.assertEqual(response.status_code, 404)
      def test_get_product_reviews(self):
            Review.objects.create(user=self.customer, product=self.product, rating=5, comment="great")
            Review.objects.create(user=self.customer2, product=self.product, rating=4, comment="ok")

            response = self.client.get(self.create_url)
            self.assertEqual(response.status_code, 200)
            
            self.assertIsInstance(response.data, list)
            self.assertEqual(len(response.data), 2)
            
            for review in response.data:
                  self.assertIn("id", review)
                  self.assertIn("user", review)
                  self.assertIn("product", review)
                  self.assertIn("rating", review)
                  self.assertIn("comment", review)
                  self.assertIn("created_at", review)

      def test_get_user_reviews(self):
            self.client.force_authenticate(self.customer)
            response = self.client.get(self.user_reviews_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['count'],0) # 0 for now
            Review.objects.create(user=self.customer, product=self.product, rating=5, comment="great")
            response = self.client.get(self.user_reviews_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['count'],1) # works
            
      def test_duplicate_review_blocked(self):
            self.client.force_authenticate(user=self.customer)
            data = {
                  "rating":5,
                  "comment":"test"
            }
            response = self.client.post(self.create_url,data)
            self.assertEqual(response.status_code, 201)
            response = self.client.post(self.create_url, data)
            self.assertEqual(response.status_code, 400)
            
      def test_rating_average_and_count(self):
            r1 = Review.objects.create(user=self.customer, product=self.product, rating=5, comment="great")
            r2 = Review.objects.create(user=self.customer2, product=self.product, rating=1, comment="nice")
            
            product_url = reverse('product-detail',kwargs={'p_id':self.product.id})
            response = self.client.get(product_url)
            self.assertEqual(response.status_code, 200)
            avg = (r1.rating+r2.rating)
            count = Review.objects.filter(product=self.product).count()
            self.assertEqual(response.data['average_rating'],avg/count) #(5+1)/2
            self.assertEqual(response.data['review_count'],count)
            
      def test_review_with_invalid_rating(self):
            self.client.force_authenticate(user=self.customer)
            data = {
                  "rating":123,
                  "comment":"test"
            }
            response = self.client.post(self.create_url,data)
            self.assertEqual(response.status_code, 400)
            
      def test_review_with_empty_comment(self):
            self.client.force_authenticate(user=self.customer)
            data = {
                  "rating":5,
                  "comment":""
            }
            response = self.client.post(self.create_url,data)
            self.assertEqual(response.status_code, 201) # we can just rate this product, comment is not neccessary
            
      def test_review_edit_after_delete(self):
            self.client.force_authenticate(user=self.customer)
            data = {
                  "rating":5,
                  "comment":"deneme"
            }
            response = self.client.post(self.create_url,data)
            self.assertEqual(response.status_code, 201)
            
            ##delete
            r_id = response.data['id']
            delete_url = reverse('review-detail', kwargs={'pk':r_id})
            response = self.client.delete(delete_url)
            self.assertEqual(response.status_code, 204)
            
            #can not edit
            
            update_url = reverse('review-detail',kwargs={'pk':r_id})
            data = {
                  "rating":1,
                  "comment":"can not update com"
            }
            response = self.client.patch(update_url, data)
            self.assertEqual(response.status_code, 404) #not found because deleted.