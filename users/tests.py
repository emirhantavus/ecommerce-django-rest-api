from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class UserTestCase(TestCase):
      def test_user_registration(self):
            url = reverse('register')
            data = {
                  'username':'test1',
                  'password':'1234567890a',
                  'email':'test1@gmail.com'
            }
            response = self.client.post(url,data)
            self.assertEqual(response.status_code, 201)
            self.assertTrue(User.object.filter(username='test1').exists())
      
      def test_missing_fields_registration(self):
            url = reverse('register')
            data = {
                  'username':'test1',
                  'email':'test1@gmail.com'
            }
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
            
      def test_empty_fields_registration(self):
            url = reverse('register')
            data = {
                  'username':'test1',
                  'password':'',
                  'email':'test1@gmail.com'
            }
            response = self.client.post(url, data)
            self.assertEqual(response.status_code,400)
            
      def test_weak_password_registration(self):
            url = reverse('register')
            data = {
                  'username':'test1',
                  'password':'123',
                  'email':'test1@gmail.com'
            }
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)