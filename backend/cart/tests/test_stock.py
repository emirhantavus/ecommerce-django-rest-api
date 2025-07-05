from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class CartStockTestCase(APITestCase):
      def setUp(self):
            self.user = User.objects.create_user(email='user@gmail.com', password='passw0rd')
            self.product = Product.objects.create(name='TestProduct', price=100, stock=2, seller=self.user)
            self.cart_url = reverse('cart-list-create')
      
      
      def test_cannot_add_product_with_zero_stock(self):
            self.product.stock = 0
            self.product.save()
            self.client.force_authenticate(user=self.user)
            data = {'product':self.product.id, 'quantity':1}
            response = self.client.post(self.cart_url, data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('out of stock',str(response.data).lower())
            
      def test_cannot_add_product_with_excess_quantity(self):
            self.product.stock = 2
            self.product.save()
            self.client.force_authenticate(user=self.user)
            data = {'product': self.product.id, 'quantity':5}
            response = self.client.post(self.cart_url, data)
            self.assertEqual(response.status_code, 400)
            self.assertIn(f"only {self.product.stock} left in stock", str(response.data).lower())