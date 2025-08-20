from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginTestCase(TestCase):
      def setUp(self):
            self.user = User.objects.create_user(
                  email='test1@gmail.com',
                  password='p1ssw2rd',
                  phone_number='xxx'   
            )
            
            self.login_url = reverse('login')
            
      def test_user_valid_login(self):
            data = {
                  'email':'test1@gmail.com',
                  'password':'p1ssw2rd',
            }
            response = self.client.post(self.login_url, data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('token', response.data) # We check token If created
            
      def test_user_login_incorrect_password(self):
            data = {
                  'email':'test1@gmail.com',
                  'password':'wr0ngpassw2rd'
            }
            response = self.client.post(self.login_url, data)
            self.assertEqual(response.status_code, 401)
            self.assertIn('detail',response.data)
            
      def test_user_login_missing_password(self):
            data = {
                  'email':'test1@gmail.com',
                  #missing password field
            }
            response = self.client.post(self.login_url, data)
            self.assertEqual(response.status_code, 400)
            self.assertNotIn('error',response.data)
            
      def test_user_login_missing_email(self):
            data = {
                  'password':'p1ssw2rd'
            }
            response = self.client.post(self.login_url, data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('email',response.data)
            
      def test_login_unregistered_email(self):
            data = {
                  'email':'unregistered@gmail.com',
                  'password':'rand0mpassW0rd'
            }
            response = self.client.post(self.login_url, data)
            self.assertEqual(response.status_code, 401)
            self.assertIn('detail',response.data)
            
      def test_login_invalid_email_format(self):
            data = {
                  'email':'invalidemail',
                  'password':'randompassw*0rd'
            }
            response = self.client.post(self.login_url, data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('email', response.data)