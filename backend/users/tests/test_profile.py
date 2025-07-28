from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import Profile
from rest_framework.test import APIClient
import json

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
            self.profile_url = reverse('profile',kwargs={'pk':self.user.profile.id})
            
      def test_login(self):
            response = self.client.post(self.login_url, self.user_login_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('token',response.data)
            
      def test_get_profile(self):
            login_response = self.client.post(self.login_url, self.user_login_data)
            self.assertEqual(login_response.status_code, 200)
            token = login_response.data['token'] # We got token
            
            profile_url = reverse('profile',kwargs={'pk':self.user.profile.id})
            response = self.client.get(profile_url, HTTP_AUTHORIZATION=f"Token {token}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['email'], 'test1@gmail.com')
            
      def test_update_profile(self):
            update_data = {
                  'seller_name':'xx_name',
                  'company_name':'yy_company'
            }
            response = self.client.put(
                  self.profile_url,
                  data=json.dumps(update_data),
                  content_type="application/json"
            )
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.data['seller_name'],'xx_name')
            self.assertEqual(response.data['company_name'],'yy_company')
            
      def test_unauthenticated_user_cannot_edit_profile(self):
            unauth_user = User.objects.create_user(
                  email='unauth@gmail.com',
                  password='asd123asd',
                  phone_number='xxx'
            )
            
            profile_url = reverse('profile', kwargs={'pk':unauth_user.profile.id})
            profile_data = {
                  'seller_name':'xxxx_name',
                  'company_name':'yyyy_name'
            }
            response = self.client.put(
                  profile_url,
                  data = ...,
                  content_type="application/json"
            )
            self.assertEqual(response.status_code, 403) #I got 403 here, LOOK HERE LATER. Need to write permission(401).
            
      def test_user_cannot_edit_another_users_profile(self):
            user1 = User.objects.create_user(
                  email='user1@gmail.com',
                  password='user1pass',
                  phone_number='user1_number'
            )
            login_response1 = self.client.post(reverse('login'),{'email':'user1@gmail.com','password':'user1pass'})
            token_user1 = login_response1.data['token'] #user1's token
            
            user2 = User.objects.create_user(
                  email='user2@gmail.com',
                  password='pass2word',
                  phone_number='user2_number'
            )
            profile_url = reverse('profile',kwargs={'pk':user2.profile.id}) # This is user2's profile id, But user1 tries to edit user2's profile data.
            hacker_profile_data = {
                  'seller_name':'hacker_name',
                  'company_name':'hacker_company' #random names xD
            }
            
            response = self.client.put(
                  profile_url,
                  data = json.dumps(hacker_profile_data),
                  content_type='application/json',
                  HTTP_AUTHORIZATION=f"Token {token_user1}"
            ) 
            
            self.assertEqual(response.status_code, 403) # DONE