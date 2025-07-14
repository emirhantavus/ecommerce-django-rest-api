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
            user = request.user
            product_id = request.data.get('product')
            quantity = int(request.data.get('quantity',1))
            if not product_id:
                  return Response({'error':'Product ID is required'},status=400)
            
            cart_item = CartItem.objects.filter(user=user, product_id=product_id)
            if cart_item.exists():
                  cart_item = cart_item.first()
                  new_quantity = cart_item.quantity + quantity
                  
                  if cart_item.product.stock < new_quantity:
                        return Response(
                              {'error': f"Only {cart_item.product.stock} left in stock, but you requested {new_quantity}."},
                              status=status.HTTP_400_BAD_REQUEST
                        )
                  cart_item.quantity = new_quantity
                  cart_item.save()
                  return Response({'message':'Cart Quantity Updated'},status=200)
            
            else:
                  serializer = CartItemSerializer(data=request.data)
                  if serializer.is_valid():
                        serializer.save(user=user)
                        return Response({'message':'Product added to cart successfuly.'},status=201)
                  return Response(serializer.errors,status=400)
      
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