from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileIntegrationTest(TestCase):
      def test_register_login_edit_profile(self):
            # 1. Create a user
            
            register_url = reverse('register')
            register_data = {
                  'email':'integrationtest2@gmail.com',
                  'password':'integ123',
                  'password2':'integ123',
                  'phone_number':'xxx'
            }
            register_reponse = self.client.post(register_url, register_data)
            self.assertEqual(register_reponse.status_code, 201)
            self.assertTrue(User.objects.filter(email='integrationtest2@gmail.com').exists())
            
            # 2. Log in with created user
            
            login_url = reverse('login')
            login_data = {
                  'email':'integrationtest2@gmail.com',
                  'password':'integ123'
            }
            login_response = self.client.post(login_url, login_data)
            self.assertEqual(login_response.status_code, 200)
            self.assertIn('token',login_response.data)
            
            # 3. Get profile info
            user = User.objects.get(email='integrationtest2@gmail.com') # get user here for profile.id 
            profile_url = reverse('profile',kwargs={'pk':user.profile.id})
            token = login_response.data.get('token')
            auth_header = f"Token {token}"
            profile_response = self.client.get(profile_url, HTTP_AUTHORIZATION=auth_header)
            self.assertEqual(profile_response.status_code,200)
            
            # 4. Edit profile
            
            profile_data = {
                  'seller_name':'ss_name',
                  'company_name':'cc_name',
            }
            import json
            print(f"Before editing: {profile_response.data}")
            profile_edit_response = self.client.put(
                  profile_url,
                  data=json.dumps(profile_data),
                  content_type='application/json',
                  HTTP_AUTHORIZATION=auth_header
            )
            self.assertEqual(profile_edit_response.status_code, 200)
            self.assertEqual(profile_edit_response.data['seller_name'], 'ss_name')
            self.assertEqual(profile_edit_response.data['company_name'], 'cc_name')
            print(f"After editing: {profile_edit_response.data}")