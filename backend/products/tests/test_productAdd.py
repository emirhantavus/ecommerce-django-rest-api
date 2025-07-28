from django.urls import reverse
from rest_framework.test import APITestCase
from products.models import Product, Category
from django.contrib.auth import get_user_model
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
User = get_user_model()

def get_image():
      image = BytesIO()
      img = Image.new('RGB', (100, 100), color=(255, 0, 0))
      img.save(image, format='JPEG')
      image.seek(0)
      return SimpleUploadedFile("test_image.jpg",image.getvalue(), content_type="image/jpeg")

class AddProductTest(APITestCase):
      def setUp(self):
            self.example_user = User.objects.create_user(
                  email="user@gmail.com",
                  password="passw0rd",
                  phone_number="xxx",
                  role="seller"
            )
            self.example_category = Category.objects.create(
                  name="phone"
            )
            
            login_data = {
                  "email":"user@gmail.com",
                  "password":"passw0rd"
            }
            login_url = reverse('login')
            login_response = self.client.post(login_url,login_data)
            self.user_token = login_response.data.get('token')
            
      def test_add_product_authenticated(self):
            image_file = get_image()
            product_data = {
                  "name":"xx_phone",
                  "description":"xx_phone description",
                  "price":129.99,
                  "stock":100,
                  "category":self.example_category.id,
                  "seller":self.example_user.id,
                  "active":True,
                  "image":image_file
            }
            product_url = reverse('products')
            auth_header = f"Token {self.user_token}"
            response = self.client.post(product_url, product_data, HTTP_AUTHORIZATION=auth_header)
            self.assertEqual(response.status_code, 201)

      def test_add_product_unauthorizated(self):
            image_file = get_image()
            product_data = {
                  "name":"xx_phone",
                  "description":"xx_phone description",
                  "price":1,
                  "stock":1,
                  "category":self.example_category.id,
                  "seller":self.example_user.id,
                  "active":True,
                  "image":image_file
            }
            product_url = reverse('products')
            response = self.client.post(product_url,product_data)
            self.assertEqual(response.status_code, 401)
            
      def test_add_product_authenticated_invalid(self):
            image_file = get_image()
            product_data = {
                  "name":"xx_phone",
                  "description":"xx_phone description",
                  "price":-5,
                  "stock":-2,
                  "category":self.example_category.id,
                  "seller":self.example_user.id,
                  "active":True,
                  "image":image_file
            }
            product_url = reverse('products')
            auth_header = f"Token {self.user_token}"
            response = self.client.post(product_url, product_data, HTTP_AUTHORIZATION=auth_header)
            self.assertEqual(response.status_code, 400) # should be bad request (400)
            
            
      ########### Also test it for [seller]