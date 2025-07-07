from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .permissions import IsCustomer, IsSellerOrAdmin

class OrderAPIView(APIView):
      permission_classes = [IsAuthenticated]
      
      def get(self, request):
            order = Order.objects.filter(user=request.user, status='paid')
            serializer = OrderSerializer(order, many=True)
            return Response(serializer.data,status.HTTP_200_OK)
      
      def post(self, request):
            serializer = OrderSerializer(data=request.data, context={'request':request})
            if serializer.is_valid():
                  order = serializer.save()
                  return Response(OrderSerializer(order).data, status.HTTP_201_CREATED)
            return Response(serializer.errors, status=400)
      
      
class UpdateOrderStatusAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      def patch(self, request, o_id):
            order = Order.objects.filter(id=o_id).first()
            if not order:
                  return Response({'error':'Order not found'},status=status.HTTP_404_NOT_FOUND)
            
            if request.user.role == 'seller':
                  has_product= False
                  for item in order.order_items.all():
                        if item.product.seller == request.user:
                              has_product = True
                              break
                  if not has_product:
                        return Response({'error': 'You cannot update another product status'}, status=status.HTTP_403_FORBIDDEN)
            
            new_status = request.data.get('status')
            valid_status = ['shipped', 'delivered','cancelled'] # for update we need 3 of them.
            
            if new_status not in valid_status:
                  return Response({'error':'Invalid status'},status.HTTP_400_BAD_REQUEST)
            
            order.status = new_status #for seller or admin.
            order.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK) 
      
class CancelOrderAPIView(APIView):
      permission_classes = [IsCustomer]
      
      def post(self, request, o_id):
            order = Order.objects.filter(id=o_id, user=request.user).first()
            
            if not order:
                  return Response({'error':'Order not found'},status=status.HTTP_404_NOT_FOUND)
            
            if order.status not in ['pending','paid']:
                  return Response({'error': 'Order cannot be cancelled at this stage.'}, status=status.HTTP_400_BAD_REQUEST)
            
            order.status = 'cancelled'
            order.save()
            return Response(OrderSerializer(order).data, status=200)