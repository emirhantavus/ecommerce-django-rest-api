from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Profile
from rest_framework.test import APIClient

User = get_user_model()

class ProfileTestCase(TestCase):
      def setUp(self):
            self.user = User.objects.create_user(
                  email='test1@gmail.com',
                  password='passw0rd',
                  phone_number='xxx'
            )
            
            self.login_url = reverse('login')
            self.user_login_data = {
                  'email':'test1@gmail.com',
                  'password':'passw0rd'
            }
            
            login_response = self.client.post(self.login_url, self.user_login_data)
            self.assertEqual(login_response.status_code, 200)
            self.assertIn("token", login_response.data)
            self.token = login_response.data['token'] ## for test_update
            
            self.client = APIClient()
            self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")
            self.profile_url = reverse('profile')
            
      def test_login(self):
            response = self.client.post(self.login_url, self.user_login_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('token',response.data)
            
      def test_get_profile(self):
            login_response = self.client.post(self.login_url, self.user_login_data)
            self.assertEqual(login_response.status_code, 200)
            token = login_response.data['token'] # We got token
            
            profile_url = reverse('profile')
            response = self.client.get(profile_url, HTTP_AUTHORIZATION=f"Token {token}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['email'], 'test1@gmail.com')
            
      def test_update_profile(self):
            import json
            update_data = {
                  'seller_name':'xx_name',
                  'company_name':'yy_company'
            }
            response = self.client.put(
                  self.profile_url,
                  data=json.dumps(update_data),
                  content_type="application/json"
            )
            print(response.data)
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.data['seller_name'],'xx_name')
            self.assertEqual(response.data['company_name'],'yy_company')