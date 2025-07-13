from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer, ReturnRequestSerializer
from .permissions import IsCustomer, IsSellerOrAdmin
from django.shortcuts import get_object_or_404
from ecommerce.utils.notifications import send_notification_and_email

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
            
            #update stock restore
            if new_status == 'cancelled':
                  for item in order.order_items.all():
                        item.product.stock += item.quantity
                        item.product.save()
                  #send mail here for info
                  send_notification_and_email(
                        user=order.user,
                        subject='Order Cancelled',
                        message=(
                              f"Dear {order.user.first_name},\n\n"
                              f"Your order (ID: {order.id}) has been cancelled."
                        ),
                        notification_type='email'
                  )
                  
            elif new_status == 'shipped':
                  send_notification_and_email(
                        user=order.user,
                        subject='Order Shipped!',
                        message=(
                            f"Dear {order.user.first_name},\n\n"
                            f"Your order (ID: {order.id}) has been shipped."
                        ),
                        notification_type='email'
                  )
            
            elif new_status == 'delivered':
                  send_notification_and_email(
                        user=order.user,
                        subject='Order Delivered!',
                        message=(
                            f"Dear {order.user.first_name},\n\n"
                            f"Your order (ID: {order.id}) has been delivered."
                        ),
                        notification_type='email'
                  )
            
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
            
            #update stock restore
            for item in order.order_items.all():
                  item.product.stock += item.quantity
                  item.product.save()
            
            send_notification_and_email(
                  user=request.user,
                  subject='Cancel Request',
                  message=(
                        f"Dear {order.user.first_name}"
                        f"Your cancellation request for order ({order.id}) has been recieved."
                  ),
                  notification_type='email'
            )
            
            order.status = 'cancelled'
            order.save()
            return Response(OrderSerializer(order).data, status=200)
      
class RequestReturnAPIView(APIView):
      permission_classes = [IsCustomer]
      
      def post(self,request,item_id):
            item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
            
            if item.order.status != 'delivered':
                  return Response({'error':'Only delivered items can be returned or exchanged'}, status=400)
            
            if item.return_status != 'none':
                  return Response({'error':'Return or exchange already requeted for this item.'},status=400)
            
            serializer = ReturnRequestSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                  serializer.save(return_status='requested')
                  #user notification
                  send_notification_and_email(
                        user=request.user,
                        subject='Return/Exchange Request Received',
                        message=f"Dear {item.order.user.first_name}, Return/Exchange Request Received for {item.product.name}",
                        notification_type='email'
                  )
                  # Seller notification
                  send_notification_and_email(
                      user=item.product.seller,
                      subject='New Return/Exchange Request',
                      message=(
                            f"Dear {item.product.seller.profile.seller_name}" # hata alırsam buraya bak !
                            f"Return/Exchange Request Received for your product {item.product.name}"
                            ),
                      notification_type='email'
                  )
                  
                  return Response(serializer.data, status=200)
            else:
                  return Response(serializer.errors, status=400)
            
      def get(self,request, item_id):
            item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
            serializer = ReturnRequestSerializer(item)
            return Response(serializer.data, status=200)
      
class ListReturnRequestsAPIView(APIView):
      permission_classes = [IsCustomer]
      
      def get(self,request):
            items = OrderItem.objects.filter(
                  order__user=request.user).exclude(return_status='none').order_by('-order__created_at')
            serializer = ReturnRequestSerializer(items, many=True)#serializer kısmını sonra genisleticez unutma.
            return Response(serializer.data,status=200)
      
class ListReturnRequestsSellerAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      def get(self, request):
            items = OrderItem.objects.filter(product__seller=request.user,return_status='requested')
            serializer = ReturnRequestSerializer(items, many=True)
            return Response(serializer.data,status=200)
      
class ProcessReturnRequestsSellerAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      def post(self,request,item_id):
            item = get_object_or_404(OrderItem, id=item_id, product__seller=request.user, return_status='requested')
            action = request.data.get('action')
            
            if action == 'approve':
                  item.return_status = 'approved'
                  if item.return_type == 'refund':
                        item.product.stock += item.quantity
                        item.product.save()
                  item.save()
                  send_notification_and_email(
                        user=item.order.user,
                        subject='Your Return Request is Approved',
                        message=(
                              f"Dear {item.order.user.first_name}, \n\n"
                              f"Your return request for product {item.product.name} has been approved."),
                        notification_type='email' 
                  )
                  serializer = ReturnRequestSerializer(item)
                  return Response(serializer.data, status=200)
            
            elif action == 'reject':
                  item.return_status = 'rejected'
                  reject_reason = request.data.get('reject_reason','')
                  if hasattr(item, 'reject_reason'):
                        item.reject_reason = reject_reason
                  item.save()
                  
                  send_notification_and_email(
                        user=item.order.user,
                        subject='Your Return Request is Rejected',
                        message=(
                              f"Dear {item.order.user.first_name}, \n\n"
                              f"Your return request for product {item.product.name} has been rejected."
                              f"Reason: {reject_reason}."
                              ),
                        notification_type='email' 
                  )
                  
                  serializer = ReturnRequestSerializer(item)
                  return Response(serializer.data,status=200)
            
            else:
                  return Response({'error':'Invalid action'},status=400)