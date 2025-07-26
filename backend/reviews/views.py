from django.shortcuts import render
from .models import Review
from .serializers import ReviewSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from products.models import Product
from order.models import OrderItem
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView

class ReviewAPIView(APIView):
      permission_classes = [IsAuthenticatedOrReadOnly]
      
      @swagger_auto_schema(request_body=ReviewSerializer)
      def post(self, request, product_id):
            product = get_object_or_404(Product,id=product_id)
            own = OrderItem.objects.filter(
                  product=product,
                  order__user=request.user,
                  order__status='delivered'
            ).exists()
            
            if not own:
                  return Response({'error':'U can only review products u bought.!'},status=403)
            
            serializer = ReviewSerializer(data=request.data, context={
                  'request':request,
                  'product':product
            })
            if serializer.is_valid():
                  serializer.save()
                  return Response({'message': f'Review posted to product id : {product_id}'},status=200)
            return Response(serializer.errors,status=400)
      
      
      def get(self,requst, product_id):
            product = get_object_or_404(Product, id=product_id)
            reviews = product.reviews.all()
            if not reviews.exists():
                  return Response({'message':'No comments yet'},status=200)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data,status=200)

class UserReviewListAPIView(ListAPIView):
      permission_classes = [IsAuthenticated]
      serializer_class = ReviewSerializer
      
      def get_queryset(self):
            return Review.objects.filter(user=self.request.user).order_by('-created_at')