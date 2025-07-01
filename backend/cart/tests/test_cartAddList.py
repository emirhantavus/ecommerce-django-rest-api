from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class CartTestCase(APITestCase):
      def setUp(self):
            self.customer = User.objects.create_user(email="customer@gmail.com",password="passw0rd",role="customer")
            self.seller = User.objects.create_user(email="seller@gmail.com",password="passw0rd",role="seller")
            self.product = Product.objects.create(name="test product",price=100,stock=5,seller=self.seller)
            self.cart_url = reverse('cart-list-create')
            
      def test_list_cart_without_authentication(self):
            response = self.client.get(self.cart_url)
            self.assertEqual(response.status_code, 401) # we get 401 error
            
      def test_list_cart_empty_with_authentication(self):
            self.client.force_authenticate(user= self.customer)
            response = self.client.get(self.cart_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 0) # empty list with auth
            
      def test_add_to_cart(self):
            self.client.force_authenticate(user= self.customer)
            response = self.client.get(self.cart_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 0)
            ## we add item then.
            data = {
                  'product': self.product.id,
                  'quantity': 2
            }
            response = self.client.post(self.cart_url,data=data)
            self.assertEqual(response.status_code,201)
            ## we control again (get method for carts)
            response = self.client.get(self.cart_url)
            self.assertEqual(response.status_code,200)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['product_name'],self.product.name)
            self.assertEqual(response.data[0]['quantity'], 2)