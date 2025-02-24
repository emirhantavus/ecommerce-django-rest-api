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
            
      def test_login(self):
            data = {
                  "email":"admin@gmail.com",
                  "password":"passw0rd"
            }
            response = self.client.post(self.login_url, data)
            self.assertEqual(response.status_code,200)
            self.assertIn('token',response.data)
            self.token = response.data['token']
            print(self.token) # Okay here.
            
      def test_add_category(self):
            data = {
                  "name":"software",
                  "parent":"django"
            }
            category_url = reverse('category')
            response = self.client.post(category_url, data)
            self.assertEqual(response.status_code, 201)
            print(response.data)