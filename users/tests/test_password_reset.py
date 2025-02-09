from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class PasswordResetTest(APITestCase):
      def setUp(self):
            self.user = User.objects.create_user(
                  email='passwordtest@gmail.com',
                  password='passw0rd',
                  phone_number='xxx'
            )
            
            self.reset_url = reverse('password_reset')
            self.confirm_url = reverse('password_confirm')
            
      def test_request_password_reset_with_valid_email(self):
            response = self.client.post(self.reset_url, {'email':self.user.email})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(mail.outbox), 1)
            
      def test_request_password_reset_with_invalid_email(self):
            response = self.client.post(self.reset_url, {'email':'invalidemail@gmail.com'})
            self.assertEqual(response.status_code, 400)
            
      def test_reset_password_with_valid_token(self):
            token = default_token_generator.make_token(self.user)
            response = self.client.post(self.confirm_url, {
                  'email':self.user.email,
                  'token':token,
                  'new_password':'newpassw0rd1'
            })
            
            self.assertEqual(response.status_code, 200)
            self.user.refresh_from_db()
            self.assertTrue(self.user.check_password('newpassw0rd1'))
            
      def test_reset_password_with_invalid_token(self):
            response = self.client.post(self.confirm_url, {
                  'email':self.user.email,
                  'token':'invalidtoken',
                  'new_password':'newpassw0rd1'
            })
            
            self.assertEqual(response.status_code, 400)
            
      def test_login_with_old_password(self):
            self.user.set_password('passw0rd')
            self.user.save()
            login_url = reverse('login')
            response = self.client.post(login_url, {'email':self.user.email, 'password':'passw0rd'})
            self.assertEqual(response.status_code, 400)
            
      def test_login_with_new_password(self):
            self.user.set_password('newpassw0rd1')
            self.user.save()
            login_url = reverse('login')
            response = self.client.post(login_url, {'email':self.user.email,'password':'newpassw0rd1'})
            self.assertEqual(response.status_code, 200)