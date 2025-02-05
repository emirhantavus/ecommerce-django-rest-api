from django.shortcuts import render
from .models import CustomUser
from .serializers import RegisterSerializer , UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout


class RegisterAPIView(APIView):
      permission_classes = [AllowAny]
      def post(self,request):
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                  user = serializer.save()
                  
                  from django.contrib.auth import login
                  login(request, user) # session
                  
                  token, created = Token.objects.get_or_create(user=user)
                  
                  return Response({
                        'message':'User created successfully',
                        'token': token.key
                        }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
      
class LoginAPIView(APIView):
      permission_classes = [AllowAny]
      def post(self,request):
            email = request.data.get('email')
            password = request.data.get('password')
            
            if not email or not password:
                  return Response({
                        'error': 'Email and password are required.'},
                        status=status.HTTP_400_BAD_REQUEST
                  )
            if '@' not in email:
                  return Response({'email':'Enter a valid email address'}, status=status.HTTP_400_BAD_REQUEST)
                  
            user = authenticate(request, email=email, password=password)
            if user is not None:
                  login(request, user)
                  token, created = Token.objects.get_or_create(user=user)
                  
                  return Response({
                        'message':'Login successful.',
                        'token':token.key
                  },status=status.HTTP_200_OK)
            else:
                  return Response({
                        'error':'unable to log in.'
                  },status=status.HTTP_400_BAD_REQUEST)
                  

class ProtectedEndpoint(APIView):
      permission_classes = [IsAuthenticated]
      
      def get(self,request):
            serializer = UserSerializer(request.user)
            return Response(serializer.data,status=status.HTTP_200_OK)