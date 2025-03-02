from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework import viewsets , status
from .models import Product, Category
from .serializers import CategorySerializer, ProductSerializer , SimpleProductSerializer
from rest_framework.permissions import AllowAny , IsAdminUser, IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import ListAPIView

class CategoryViewSet(viewsets.ModelViewSet):
      queryset = Category.objects.all()
      serializer_class = CategorySerializer
      permission_classes = [IsAdminUser] # change it later.
      
class ProductAPIView(APIView, LimitOffsetPagination):
      def get_permissions(self):
            if self.request.method == 'POST':
                  return [IsAuthenticated()]
            return [AllowAny()]

      def get(self,request):
            queryset = Product.objects.select_related('seller','category').prefetch_related('seller__products')
            
            seller_id = request.query_params.get("seller")
            if seller_id:
                  queryset = queryset.filter(seller=seller_id)
                  
            category_id = request.query_params.get("category")
            if category_id == 'null':
                  queryset = queryset.filter(category__isnull=True)
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
                  
            #pagination here
            results = self.paginate_queryset(queryset, request, view=self)
            if results is not None:
                  serializer = ProductSerializer(results, many=True)
                  return self.get_paginated_response(serializer.data)
                  
            serializer = ProductSerializer(queryset, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
      
      def post(self,request):
            serializer = ProductSerializer(data=request.data, context={'request':request})
            if serializer.is_valid():
                  serializer.save()
                  return Response({'message':'Product added.'},status=status.HTTP_201_CREATED)
            return Response({'errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
      
      
class SellerProductsListView(ListAPIView):
      serializer_class = SimpleProductSerializer
      permission_classes = [AllowAny]
      
      def get_queryset(self):
            seller_id = self.kwargs['seller_id']
            if not seller_id:
                  raise ValueError("Not found Seller ID.")
            return Product.objects.filter(seller_id=seller_id)