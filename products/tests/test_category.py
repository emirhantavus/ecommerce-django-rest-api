from django.urls import reverse
from rest_framework.test import APITestCase
from ..models import Category
from django.contrib.auth import get_user_model

User = get_user_model()

class AddCategoryTest(APITestCase):
      def setUp(self):
            self.admin_user = User.objects.create_superuser(
                  email='admin@gmail.com',
                  password='passw0rd',
                  phone_number='xxx'
            )
            self.login_url = reverse('login')
            self.parent_category = Category.objects.create(name="django")
            
            login_data_admin = {
                  "email":"admin@gmail.com",
                  "password":"passw0rd"
            }
            response_admin = self.client.post(self.login_url, login_data_admin)
            self.admin_token = response_admin.data.get('token')
            
            self.user = User.objects.create_user(
                  email="user@gmail.com",
                  password="passw0rd",
                  phone_number="xxx"
            )
            login_data_user = {
                  "email":"user@gmail.com",
                  "password":"passw0rd"
            }
            
            response_user = self.client.post(self.login_url, login_data_user)
            self.user_token = response_user.data.get('token')
            
      def test_add_category_admin(self):
            data = {
                  "name":"software",
                  "parent":self.parent_category.id
            }
            category_url = reverse('category-list')
            auth_header = f"Token {self.admin_token}"
            response = self.client.post(category_url, data, HTTP_AUTHORIZATION=auth_header)
            self.assertEqual(response.status_code, 201)
            print(response.data)
            
      def test_add_category_not_admin(self):
            data = {
                  "name":"hardware",
                  "parent":self.parent_category.id
            }
            category_url = reverse('category-list')
            auth_header = f"Token {self.user_token}"
            response = self.client.post(category_url, data, HTTP_AUTHORIZATION=auth_header)
            self.assertEqual(response.status_code, 403) #We need to get 403 status here.
            print(response.data)