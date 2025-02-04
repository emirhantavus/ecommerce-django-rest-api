from django.shortcuts import render
from .models import CustomUser
from .serializers import RegisterSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.authtoken.models import Token


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