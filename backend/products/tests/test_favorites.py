from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product , Category , Favorites
from django.urls import reverse


User = get_user_model()

class FavoritesTestCase(APITestCase):
      def setUp(self):
            self.category = Category.objects.create(name="cat")
            self.seller = User.objects.create_user(email="seller@gmail.com",password="passw0rd",role="seller")
            self.my_account = User.objects.create_user(email="myaccount@gmail.com",password="passw0rd",role="customer")
            self.another_account  = User.objects.create_user(email="another@gmail.com",password="passw0rd",role="customer")
            self.product_one = Product.objects.create(name="test product 1",price=100,stock=5,seller=self.seller)
            self.product_two = Product.objects.create(name="test product 2",price=50,stock=10,seller=self.seller)
            self.product_three = Product.objects.create(name="test product 3",price=20,stock=20,seller=self.seller)
            
            self.login_url = reverse('login')
            self.product_url = reverse('products')
            self.fav_url = reverse('favorites')
            
            login_my_data = {
                  "email":"myaccount@gmail.com",
                  "password":"passw0rd"
            }
            my_response = self.client.post(self.login_url, login_my_data)
            my_token = my_response.data.get('token')
            self.my_auth_header = f"Token {my_token}"
            
            login_another_data = {
                  "email":"another@gmail.com",
                  "password":"passw0rd"
            }
            another_response = self.client.post(self.login_url, login_another_data)
            another_token = another_response.data.get('token')
            self.another_auth_header = f"Token {another_token}"
            
      def test_add_favorite_item(self):
            data = {
                  "product_id":self.product_one.id
            }
            response = self.client.post(self.fav_url ,data, HTTP_AUTHORIZATION=self.my_auth_header)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(Favorites.objects.count(),1)
            
            data = {
                  "product_id":self.product_two.id
            }
            response = self.client.post(self.fav_url ,data, HTTP_AUTHORIZATION=self.my_auth_header)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(Favorites.objects.count(),2)
            
      def test_get_favorite_items(self):
            data = {
                  "product_id":self.product_one.id
            }
            self.client.post(self.fav_url ,data, HTTP_AUTHORIZATION=self.my_auth_header)
            data = {
                  "product_id":self.product_two.id
            }
            self.client.post(self.fav_url ,data, HTTP_AUTHORIZATION=self.my_auth_header)
            
            response = self.client.get(self.fav_url, HTTP_AUTHORIZATION=self.my_auth_header)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Favorites.objects.filter(user=self.my_account).count(), 2)
            
      def test_control_get_favorite_items(self):
            data = {
                  "product_id":self.product_one.id
            }
            self.client.post(self.fav_url ,data, HTTP_AUTHORIZATION=self.my_auth_header)
            
            data = {
                  "product_id":self.product_two.id
            }
            self.client.post(self.fav_url ,data, HTTP_AUTHORIZATION=self.another_auth_header)
            
            response = self.client.get(self.fav_url, HTTP_AUTHORIZATION=self.my_auth_header)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Favorites.objects.filter(user=self.my_account).count(),1) # It works. We get only our fav items.
            self.assertEqual(Favorites.objects.all().count(), 2) # there are 2 items but my_acc has only 1 item.
            
      def test_not_get_anothers_favorite_items(self):
            datas = {
                  "one":{
                        "product_id":self.product_one.id},
                  "two":{
                        "product_id":self.product_two.id}}
            self.client.post(self.fav_url, datas["one"], HTTP_AUTHORIZATION=self.another_auth_header)
            self.client.post(self.fav_url, datas["two"], HTTP_AUTHORIZATION=self.another_auth_header)
            
            response = self.client.get(self.fav_url, HTTP_AUTHORIZATION=self.my_auth_header)
            self.assertEqual(Favorites.objects.filter(user=self.another_account).count(), 2)
            
            self.assertNotIn(
                  datas["one"]["product_id"], [item["product_id"] for item in response.data]
            )
            
            self.assertNotIn(
                  datas["two"]["product_id"], [item["product_id"] for item in response.data]
            )
            
      def test_delete_favorite_item(self):
            data = {"product_id":self.product_one.id}
            response = self.client.post(self.fav_url, data, HTTP_AUTHORIZATION=self.my_auth_header)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(Favorites.objects.filter(user=self.my_account).count(), 1)

            favorite = Favorites.objects.get(user=self.my_account, product=self.product_one)
            fav_del_url = reverse('favorite-delete', kwargs={'favorite_id':favorite.id})
            
            response = self.client.delete(fav_del_url, HTTP_AUTHORIZATION=self.my_auth_header)
            self.assertEqual(response.status_code, 204)
            self.assertEqual(Favorites.objects.filter(user=self.my_account).count(), 0)