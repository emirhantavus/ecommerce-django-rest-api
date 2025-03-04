from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework import viewsets , status
from .models import Product, Category
from .serializers import CategorySerializer, ProductSerializer , SimpleProductSerializer
from rest_framework.permissions import AllowAny , IsAdminUser, IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import ListAPIView , RetrieveAPIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.views.decorators.vary import vary_on_headers
from django.shortcuts import get_object_or_404

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
            queryset = Product.objects.select_related('seller','category').prefetch_related('seller__products').order_by('pk')
            
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
            
            #################
            
            search_query = request.query_params.get("search")
            if search_query:
                  queryset = queryset.filter(name__icontains=search_query)
                  
            #pagination here
            results = self.paginate_queryset(queryset, request, view=self)
            if results is not None:
                  serializer = ProductSerializer(results, many=True)
                  return self.get_paginated_response(serializer.data)
                  
            serializer = ProductSerializer(queryset, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
      
      def post(self,request):
            if request.user.role == "seller": #only sellers can add items.
                  serializer = ProductSerializer(data=request.data, context={'request':request})
                  if serializer.is_valid():
                        serializer.save()
                        return Response({'message':'Product added.'},status=status.HTTP_201_CREATED)
            else:
                  return Response({'message':'Only sellers can add products.'},status=status.HTTP_403_FORBIDDEN)
            return Response({'errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
      
      
      

@method_decorator(cache_page(60*30, key_prefix='seller_products'),name='dispatch')
class SellerProductsListView(ListAPIView):
      serializer_class = SimpleProductSerializer
      permission_classes = [AllowAny]
      
      def get_queryset(self):
            import time
            print("2 saniye bekleniyor") # simdilik kalsın sonra sil.
            time.sleep(2)
            seller_id = self.kwargs['seller_id']
            if not seller_id:
                  raise ValueError("Not found Seller ID.")
            return Product.objects.filter(seller_id=seller_id).order_by('pk')
      
      
class ProductUpdateAPIView(APIView):
      permission_classes = [IsAuthenticated]
      
      def get_object(self, pk):
            product = get_object_or_404(Product, pk=pk)
            if product.seller != self.request.user:
                  return Response({'message':'U can not edit this product.'},status=status.HTTP_403_FORBIDDEN)
            return product
      
      def put(self,request,pk):
            product = self.get_object(pk)
            if isinstance(product, Response):
                  return product
            
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                  serializer.save()
                  return Response({'message':'Product edited successfuly','product':serializer.data},status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
      
      def patch(self,request,pk):
            product = self.get_object(pk)
            if isinstance(product, Response):
                  return product
            
            serializer = ProductSerializer(product, data= request.data, partial=True) #partial for edit only for 1 field.
            if serializer.is_valid():
                  serializer.save()
                  return Response({'message':'Product edited successfuly'},status=status.HTTP_200_OK)
            return Response({'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
      
      
class ProductDetailAPIView(RetrieveAPIView):
      queryset = Product.objects.all()
      serializer_class = ProductSerializer
      permission_classes = [AllowAny]