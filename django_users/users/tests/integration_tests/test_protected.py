from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthIntegrationTest(TestCase):
      def test_register_login_protected_endpoint(self):
            # 1. Create a user
            
            register_url = reverse('register')
            register_data = {
                  'email':'integrationtest1@gmail.com',
                  'password':'integ123',
                  'password2':'integ123',
                  'phone_number':'xxx'
            }
            register_reponse = self.client.post(register_url, register_data)
            self.assertEqual(register_reponse.status_code, 201)
            self.assertTrue(User.objects.filter(email='integrationtest1@gmail.com').exists())
            
            # 2. Log in with created user
            
            login_url = reverse('login')
            login_data = {
                  'email':'integrationtest1@gmail.com',
                  'password':'integ123'
            }
            login_response = self.client.post(login_url, login_data)
            self.assertEqual(login_response.status_code, 200)
            self.assertIn('token',login_response.data)
            
            # 3. Test protected endpoint with token
            
            protected_url = reverse('protected')
            token = login_response.data.get('token')
            auth_header = f"Token {token}"
            protected_response = self.client.get(protected_url, HTTP_AUTHORIZATION=auth_header)
            self.assertEqual(protected_response.status_code, 200)