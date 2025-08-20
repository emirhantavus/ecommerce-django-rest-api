from django.shortcuts import render
from .models import CustomUser , Profile
from .serializers import (RegisterSerializer , UserSerializer , ProfileSerializer,
                          PasswordResetSerializer, PasswordResetConfirmSerializer, LoginSerializer)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.authentication import TokenAuthentication
from drf_yasg.utils import swagger_auto_schema
from utils.pagination import UsersCursorPagination
from rest_framework.throttling import ScopedRateThrottle

class RegisterAPIView(APIView):
      permission_classes = [AllowAny]
      serializer_class = RegisterSerializer
      @swagger_auto_schema(request_body=RegisterSerializer)
      def post(self,request):
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                  serializer.save()
                  return Response({
                        'message':'User created successfully',
                        }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
      
class LoginAPIView(APIView):
      permission_classes = [AllowAny]
      serializer_class = LoginSerializer
      
      @swagger_auto_schema(request_body=LoginSerializer)
      def post(self,request):
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
                  
            user = authenticate(request, email=email, password=password)
            
            if user is None:
                  return Response({'detail':'Invalid email or password'},status=401)
            
            if not user.is_active:
                  return Response({'detail':'Account is inactive'},status=403)

            token, _ = Token.objects.get_or_create(user=user) ##later i may change it.
            return Response({
                  'message':'Login successful',
                  'token':token.key,
                  'user':{'id':user.id, 'email':user.email}
            }, status=status.HTTP_200_OK)
            
            
class AllUsersAPIView(APIView, UsersCursorPagination):
      permission_classes = [IsAdminUser]
      throttle_classes = [ScopedRateThrottle]
      throttle_scope = 'login'
      
      def get(self,request):
            users = CustomUser.objects.all()
            pag_qs = self.paginate_queryset(users, request, view=self)
            serializer = UserSerializer(pag_qs, many=True)
            return self.get_paginated_response(serializer.data)
      
      
class ProfileAPIView(APIView):
      permission_classes = [IsAuthenticated]

      def get(self,request,pk):
            profile = get_object_or_404(Profile, id=pk)
            serializer = ProfileSerializer(profile)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
      
      @swagger_auto_schema(request_body=ProfileSerializer)
      def put(self,request,pk):
            profile = get_object_or_404(Profile,id=pk)
            if profile.user != request.user:
                  return Response({'error':"U can not edit another's profile."},status=status.HTTP_403_FORBIDDEN)
            
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                  serializer.save()
                  return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
      
class PasswordResetView(APIView):
      permission_classes = [AllowAny]
      
      @swagger_auto_schema(request_body=PasswordResetSerializer)
      def post(self, request):
            serializer = PasswordResetSerializer(data=request.data)
            if serializer.is_valid():
                  email = serializer.validated_data['email']
                  user = CustomUser.objects.filter(email=email).first()
                  
                  if not user:
                        return Response({'error':'User with this email does not exist.'},status=status.HTTP_400_BAD_REQUEST)
                  
                  token = default_token_generator.make_token(user)
                  reset_link = f"http://localhost:8000/password-reset-confirm?token={token}&email={email}"
                  
                  send_mail(
                        "Password Reset Request",
                        f"Click the link to reset your password: \n\n{reset_link}",
                        "deneme@gmail.com",
                        [email],
                        fail_silently=False,
                  )
                  return Response({'message':'Password reset request received. Check your email'},status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                  

class PasswordResetConfirmView(APIView):
      permission_classes = [AllowAny]
      
      @swagger_auto_schema(request_body=PasswordResetConfirmSerializer)
      def post(self, request):
            serializer = PasswordResetConfirmSerializer(data=request.data)
            if serializer.is_valid():
                  email = serializer.validated_data['email']
                  token = serializer.validated_data['token']
                  new_pass = serializer.validated_data['new_password']
                  
                  user = get_object_or_404(CustomUser, email=email)
                  if default_token_generator.check_token(user, token):
                        user.set_password(new_pass)
                        user.save()
                        return Response({'message':'Password is changed successfully.'},status=status.HTTP_200_OK)
                  return Response({'error':'Invalid or expired token.!'},status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
      
      
#############################################################################################################
#############################################################################################################

class CheckTokenAPIView(APIView):
      permission_classes = [IsAuthenticated]
      authentication_classes = [TokenAuthentication]
      def get(self, request):
            return Response({"user_id":request.user.id,"is_valid":True})