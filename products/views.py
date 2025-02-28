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
            queryset = Product.objects.all()
            
            seller_id = request.query_params.get("seller")
            if seller_id:
                  queryset = queryset.filter(seller=seller_id)
                  
            category_id = request.query_params.get("category")
            if category_id == 'null':
                  queryset = queryset.filter(category_isnull=True)
            elif category_id:
                  queryset = queryset.filter(category=category_id)
                  
            stock_filter = request.query_params.get("stock")
            if stock_filter == '0':
                  queryset = queryset.filter(stock=0)
            elif stock_filter == "1":
                  queryset = queryset.filter(stock__gt=0)
                  
            discount_filter = request.query_params.get("discount")
            if discount_filter == 'true':
                  queryset = queryset.filter(discount=True)
            elif discount_filter == 'false':
                  queryset = queryset.filter(discount=False)
                  
            serializer = ProductSerializer(queryset, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
      
      def post(self,request):
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                  serializer.save()
                  return Response({'message':'Product added.'},status=status.HTTP_201_CREATED)
            return Response({'errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)