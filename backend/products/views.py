from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework import viewsets , status
from .models import Product, Category , Favorites
from .serializers import CategorySerializer, ProductSerializer , SimpleProductSerializer , FavoritesSerializer
from rest_framework.permissions import AllowAny , IsAdminUser, IsAuthenticated
from rest_framework.generics import ListAPIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
import re
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Avg, Count, Exists, OuterRef, Value, BooleanField
from utils.pagination import ProductCursorPagination

class CategoryViewSet(viewsets.ModelViewSet):
      queryset = Category.objects.all()
      serializer_class = CategorySerializer
      permission_classes = [IsAdminUser] # change it later.
      
class ProductAPIView(APIView, ProductCursorPagination):
      def get_permissions(self):
            if self.request.method == 'POST':
                  return [IsAuthenticated()]
            return [AllowAny()]

      def get(self,request):
            queryset = Product.objects.select_related('seller','category').order_by('id')
            
            seller_id = request.query_params.get("seller")
            if seller_id:
                  queryset = queryset.filter(seller=int(seller_id))
                  
            category_name = request.query_params.get("category")
            if category_name == 'null':
                  queryset = queryset.filter(category__isnull=True)
            elif category_name:
                  try:
                        category = Category.objects.get(name=category_name)
                        category_data = CategorySerializer(category).data
                        def sub_category_ids(category_data):
                              ids = [category_data['id']]
                              for subcat in category_data['subcategories']:
                                    ids.extend(sub_category_ids(subcat))
                              return ids
                        all_category_ids = sub_category_ids(category_data)
                        queryset = queryset.filter(category__id__in=all_category_ids)
                  except Category.DoesNotExist:
                        queryset = queryset.none()
                  
            in_stock = request.query_params.get("stock")
            if in_stock == '0':
                  queryset = queryset.filter(stock=0)
            elif in_stock == "1":
                  queryset = queryset.filter(stock__gt=0)
                  
            discount_filter = request.query_params.get("discount")
            if discount_filter is not None:
                  discount_filter = discount_filter.lower() == 'true'
                  queryset = queryset.filter(discount=discount_filter)
            
            #################
            
            search_query = request.query_params.get("search")
            if search_query:
                  if not re.match(r'^[a-zA-Z0-9 ]+$', search_query):
                        return Response({'error':'Invalid search query'},status=status.HTTP_400_BAD_REQUEST)
                  queryset = queryset.filter(name__icontains=search_query)
                  
            min_price = request.query_params.get("min_price")
            max_price = request.query_params.get("max_price")
            
            if min_price:
                  queryset = queryset.filter(price__gte=min_price)
            if max_price:
                  queryset = queryset.filter(price__lte=max_price)
                  
            ######
            sort_by = request.query_params.get("sort_by")
            order = request.query_params.get("order","asc")
            
            sort_fields = ["price","created_at","stock"]
            
            if sort_by in sort_fields:
                  if order == 'desc':
                        sort_by = f"-{sort_by}"
                  queryset = queryset.order_by(sort_by)
            ######
            
            qs = queryset.annotate(
                  average_rating=Avg('reviews__rating'),
                  review_count= Count('reviews', distinct=True)
            )
            
            user = request.user
            if user.is_authenticated:
                  fav = Favorites.objects.filter(user=user, product_id=OuterRef('pk'))
                  qs = qs.annotate(is_favorited=Exists(fav))
            else:
                  qs = qs.annotate(is_favorited=Value(False, output_field=BooleanField()))
            
            #pagination here
            results = self.paginate_queryset(qs, request, view=self)
            if results is not None:
                  serializer = ProductSerializer(results, many=True)
                  return self.get_paginated_response(serializer.data)
                  
            serializer = ProductSerializer(qs, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
      
      @swagger_auto_schema(request_body=ProductSerializer)
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
      
      
class ProductUpdateDeleteAPIView(APIView):
      permission_classes = [IsAuthenticated]
      
      def get_object(self, request, pk):
            product = get_object_or_404(Product, pk=pk)
            if product.seller != request.user:
                  if request.method in ['PUT','PATCH']:
                        return Response({'message':'U can not edit this product.'},status=status.HTTP_403_FORBIDDEN)
                  elif request.method == 'DELETE':
                        return Response({'message':'U can not delete this product.'},status=status.HTTP_403_FORBIDDEN)
            return product
      
      @swagger_auto_schema(request_body=ProductSerializer)
      def put(self,request,pk):
            product = self.get_object(request, pk)
            if isinstance(product, Response):
                  return product
            
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                  serializer.save()
                  return Response({'message':'Product edited successfuly','product':serializer.data},status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
      
      @swagger_auto_schema(request_body=ProductSerializer)
      def patch(self,request,pk):
            product = self.get_object(request, pk)
            if isinstance(product, Response):
                  return product
            
            serializer = ProductSerializer(product, data= request.data, partial=True) #partial for edit only for 1 field.
            if serializer.is_valid():
                  serializer.save()
                  return Response({'message':'Product edited successfuly'},status=status.HTTP_200_OK)
            return Response({'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
      
      def delete(self,request, pk):
            product = self.get_object(request, pk)
            if isinstance(product, Response):
                  return product
            
            product.delete()
            return Response({'message':'product deleted.'},status=status.HTTP_204_NO_CONTENT)
      
      
class ProductDetailAPIView(APIView):
      permission_classes = [AllowAny]
      def get(self, request, p_id):
            product = get_object_or_404(
                  Product.objects.annotate(
                        average_rating=Avg('reviews__rating'),
                        review_count=Count('reviews',distinct=True)
                  ),
                  id=p_id
            )
            serializer = ProductSerializer(product,context={'request':request})
            return Response(serializer.data)
      
class FavoritesAPIView(APIView):
      permission_classes = [IsAuthenticated]
      
      def get(self,request):
            favs = Favorites.objects.filter(user=request.user)
            serializer = FavoritesSerializer(favs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
      
      @swagger_auto_schema(request_body=FavoritesSerializer)
      def post(self,request):
            product_id = request.data.get("product_id")
            product = get_object_or_404(Product, id=product_id)
            
            if Favorites.objects.filter(user=request.user, product=product).exists():
                  return Response({'message':'This product is already in your favorites'},status=status.HTTP_400_BAD_REQUEST)
            
            favorite = Favorites.objects.create(user=request.user, product = product)
            serializer = FavoritesSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
      
      def delete(self,request,favorite_id):
            fav = get_object_or_404(Favorites,user=request.user,id=favorite_id)
            fav.delete()
            return Response({'message':'Favorite item deleted.'},status=status.HTTP_204_NO_CONTENT)