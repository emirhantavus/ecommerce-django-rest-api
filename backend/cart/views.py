from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CartItem
from .serializers import CartItemSerializer
from django.shortcuts import get_object_or_404

class CartItemCreateListAPIView(APIView):
      permission_classes = [IsAuthenticated]
      
      def get(self, request):
            user = request.user
            cartItems = CartItem.objects.filter(user=user)
            serializer = CartItemSerializer(cartItems, many=True)
            total = sum(cart.get_total_price for cart in cartItems)
            return Response({
                  'items':serializer.data,
                  'total_cart_price': total
            },status.HTTP_200_OK)
      
      def post(self,request):
            serializer = CartItemSerializer(data=request.data)
            if serializer.is_valid():
                  serializer.save(user=request.user)
                  return Response({'message':'Product added to cart successfuly'},status.HTTP_201_CREATED)
            return Response(serializer.errors)
      
class CartItemRetrieveOrDestroyAPIView(APIView):
      permission_classes = [IsAuthenticated]
      
      def put(self, request, id):
            cartItem = get_object_or_404(CartItem, id=id, user=request.user)
            serializer = CartItemSerializer(cartItem, data= request.data, partial=True)
            if serializer.is_valid():
                  serializer.save()
                  return Response({'message':'CartItem updated'}, status.HTTP_200_OK)
            return Response({'message':serializer.errors},status.HTTP_400_BAD_REQUEST)
      
      def delete(self, request,id):
            cartItem = get_object_or_404(CartItem,id=id, user=request.user)
            cartItem.delete()
            return Response({'message':'Item deleted from cart'},status.HTTP_204_NO_CONTENT)