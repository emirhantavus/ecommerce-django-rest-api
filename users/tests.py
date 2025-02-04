from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTestCase(TestCase):
      def test_user_registration(self):
            url = reverse('register')
            data = {
                  'email':'test1@gmail.com',
                  'password':'str123ong567pass',
                  'password2':'str123ong567pass',
                  'phone_number':'xxx'
            }
            response = self.client.post(url,data)
            self.assertEqual(response.status_code, 201)
            self.assertTrue(User.objects.filter(email='test1@gmail.com').exists())
            self.assertNotIn('error', response.data)
      
      def test_missing_fields_registration(self):
            url = reverse('register')
            data = {
                  'email':'test2@gmail.com',
                  'phone_number':'xxx'
            }
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('password', response.data)
            
      def test_empty_fields_registration(self):
            url = reverse('register')
            data = {
                  'email':'test3@gmail.com',
                  'password':'1234567890',
                  'password2':'',
                  'phone_number':'xxx'
            }
            response = self.client.post(url, data)
            self.assertEqual(response.status_code,400)
            
      def test_weak_password_registration(self):
            url = reverse('register')
            data = {
                  'email':'test4@gmail.com',
                  'password':'123',
                  'password2':'123',
                  'phone_number':'xxx'
            }
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('password', response.data)
            
      def test_password_mismatch(self):
            url = reverse('register')
            data = {
                  'email': 'test5@gmail.com',
                  'password': 'ran123dom123pass345',
                  'password2': 'wrongpassword',
                  'phone_number': 'xxx'
            }
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('password',response.data)
            
      def test_duplicate_email_registration(self):
            url = reverse('register')
            data = {
                  'email': 'test6@gmail.com',
                  'password': 'asdasdas',
                  'password2': 'asdasdas',
                  'phone_number': 'xxx'
            }
            self.client.post(url, data) # first registration
            
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('email', response.data)
            
            
      def test_password_hashing(self):
            url = reverse('register')
            data = {
                'email': 'test7@gmail.com',
                'password': 'deneme123',
                'password2': 'deneme123',
                'phone_number': 'xxx'
            }
            response = self.client.post(url, data),
            user = User.objects.get(email='test7@gmail.com')
            self.assertNotEqual(user.password, 'deneme123') # OK password is hashed