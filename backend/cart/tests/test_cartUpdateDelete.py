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
            self.cart_ls_url = reverse('cart-list-create')
            
      def test_delete_cart_item_without_authentication(self):
            self.client.force_authenticate(user=self.customer)
            data = {
                  'product': self.product.id,
                  'quantity': 2
            }
            response = self.client.post(self.cart_ls_url,data=data)
            self.assertEqual(response.status_code,201)
            response = self.client.get(self.cart_ls_url)
            self.client.logout()# logout here, we authenticate for adding item to cart
            response = self.client.delete(reverse('cart-update-delete', kwargs={'id':response.data[0]['id']}))
            self.assertEqual(response.status_code, 401) # we get 401 error
            
      def test_delete_cart_item_with_authentication(self):
            self.client.force_authenticate(user= self.customer)
            data = {
                  'product': self.product.id,
                  'quantity': 2
            }
            response = self.client.post(self.cart_ls_url,data=data)
            self.assertEqual(response.status_code,201)
            response = self.client.get(self.cart_ls_url)
            self.assertEqual(response.status_code,200)
            self.assertEqual(len(response.data), 1)
            cart_item_id = response.data[0]['id'] #we get item id here.
            url = reverse('cart-update-delete', kwargs={'id':cart_item_id})
            response = self.client.delete(url)
            self.assertEqual(response.status_code, 204) # if 204 then ok we deleted it.
            
      def test_add_to_cart(self):
            self.client.force_authenticate(user= self.customer)
            response = self.client.get(self.cart_ls_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data), 0)
            ## add item
            data = {
                  'product': self.product.id,
                  'quantity': 2
            }
            response = self.client.post(self.cart_ls_url,data=data)
            self.assertEqual(response.status_code,201)
            response = self.client.get(self.cart_ls_url)
            cart_id = response.data[0]['id']
            self.assertEqual(response.data[0]['quantity'],2)
            ## update item
            update_url = reverse('cart-update-delete', kwargs={'id':cart_id})
            new_Data = {
                  'quantity':5
            }
            response = self.client.put(update_url, new_Data) # we update here
            self.assertEqual(response.status_code, 200)
            #we check here quantity
            response = self.client.get(self.cart_ls_url)
            self.assertEqual(response.data[0]['quantity'],5)