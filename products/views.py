from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework import viewsets , status
from .models import Product, Category
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.permissions import AllowAny , IsAdminUser, IsAuthenticated

class CategoryViewSet(viewsets.ModelViewSet):
      queryset = Category.objects.all()
      serializer_class = CategorySerializer
      permission_classes = [IsAdminUser]
      
class ProductAPIView(APIView):
      permission_classes = [IsAuthenticated]
      def get(self,request):
            product = Product.objects.all()
            serializer = ProductSerializer(product,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
      
      def post(self,request):
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                  serializer.save()
                  return Response({'message':'Product added.'},status=status.HTTP_201_CREATED)
            return Response({'errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)