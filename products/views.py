from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Product, Category
from .serializers import CategorySerializer
from rest_framework.permissions import AllowAny , IsAdminUser

class CategoryViewSet(viewsets.ModelViewSet):
      queryset = Category.objects.all()
      serializer_class = CategorySerializer
      permission_classes = [IsAdminUser]
      
class deneme(APIView):
      permission_classes = [AllowAny]
      def get(self,request):
            return Response({'message':'denemeee'})