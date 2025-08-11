from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import (OrderSerializer, ReturnRequestSerializer,
                          OrderHistoryCustomerSerializer, OrderHistorySellerSerializer ,OrderItemSerializer)
from .permissions import IsCustomer, IsSellerOrAdmin
from django.shortcuts import get_object_or_404
from ecommerce.utils.notifications import send_notification_and_email
from drf_yasg.utils import swagger_auto_schema
from order.services.shipment_service import create_shipment

class OrderAPIView(APIView):
      permission_classes = [IsAuthenticated]
      
      def get(self, request):
            order = Order.objects.filter(user=request.user, status='paid')
            serializer = OrderSerializer(order, many=True)
            return Response(serializer.data,status.HTTP_200_OK) #Unnecessary here !!
      
      @swagger_auto_schema(request_body=OrderSerializer)
      def post(self, request):
            serializer = OrderSerializer(data=request.data, context={'request':request})
            if serializer.is_valid():
                  order = serializer.save()
                  return Response(OrderSerializer(order).data, status.HTTP_201_CREATED)
            return Response(serializer.errors, status=400)
      
      
class ShipOrderItemAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      def post(self,request,item_id):
            item = get_object_or_404(OrderItem,id=item_id)
            if item.product.seller != request.user:
                  return Response({'error':'U can not ship another seller.s product'},status=403)
            if item.tracking_number:
                  return Response({'error':'Already shipped !'},status=400)
            
            result = create_shipment(item)
            
            if 'error' in result:
                  return Response({'error':result['error']},status=500)
            else:
                  send_notification_and_email(
                        user=item.order.user,
                        subject='Your Order Has Been Shipped!',
                        message=f"Your product '{item.product.name}' has been shipped. Tracking Number: {item.tracking_number}",
                        notification_type='email'
                  )
                  return Response({
                        'success':True,
                        'tracking_number': item.tracking_number,
                        'shipment':result
                  },status=201)
      
class CancelOrderAPIView(APIView):
      permission_classes = [IsCustomer]
      
      @swagger_auto_schema(request_body=None)
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
      
      @swagger_auto_schema(request_body=ReturnRequestSerializer)
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
            status_param = request.query_params.get('status')
            items = OrderItem.objects.filter(
                  order__user=request.user).exclude(return_status='none').order_by('-order__created_at')
            
            if status_param:
                  items = items.filter(return_status=status_param)
            else:
                  items=items.filter(return_status='requested')
                  
            serializer = ReturnRequestSerializer(items, many=True)#serializer kısmını sonra genisleticez unutma.
            return Response(serializer.data,status=200)
      
class ListReturnRequestsSellerAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      def get(self, request):
            status_param = request.query_params.get('status')
            items = OrderItem.objects.filter(product__seller=request.user).exclude(return_status='none')
            
            if status_param:
                  items = items.filter(return_status=status_param)
            else:
                  items = items.filter(return_status='requested')
            serializer = ReturnRequestSerializer(items, many=True)
            return Response(serializer.data,status=200)
      
class ProcessReturnRequestsSellerAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      @swagger_auto_schema(request_body=None)
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
            
            
class OrderHistoryListAPIView(APIView):
      permission_classes = [IsCustomer]
      
      def get(self,request):
            orders = Order.objects.filter(user=request.user,status__in=['delivered','cancelled'])
            serializer = OrderHistoryCustomerSerializer(orders,many=True)
            return Response(serializer.data,status=200)
      
      
class OrderHistoryDetailAPIView(APIView):
      permission_classes = [IsCustomer]
      
      def get(self,request,o_id):
            order = get_object_or_404(Order,user=request.user,id=o_id)
            serializer = OrderHistoryCustomerSerializer(order)
            return Response(serializer.data,status=200)
      
class OrderHistorySellerAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      def get(self,request):
            items = OrderItem.objects.filter(product__seller=request.user,order__status='delivered').order_by('-order__created_at')
            serializer = OrderHistorySellerSerializer(items, many=True)
            return Response(serializer.data,status=200)
      
class ActiveOrderListAPIView(APIView):
      permission_classes = [IsCustomer]
      
      def get(self,request):
            orders = Order.objects.filter(
                  user=request.user,
                  status__in=['pending','paid','shipped']
            ).order_by('-created_at')
            serializer = OrderHistoryCustomerSerializer(orders,many=True)
            return Response(serializer.data,status=200)
      
      
class SellerOrderItemsNotShippedAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      def get(self,request):
            items = OrderItem.objects.filter(
                  product__seller=request.user,
                  order__status='paid',
                  tracking_number__isnull=True
                  ).order_by('-order__created_at')
            
            serializer = OrderItemSerializer(items,many=True)
            return Response(serializer.data,status=200)
      
      
      
##### Shipment status Send_mail Webhook

class ShipmentStatusWebhookAPIView(APIView):
      permission_classes = [AllowAny,] # I will change it LATER !!!! NOT FORGET
      
      def post(self,request):
            tracking_number = request.data.get('tracking_number')
            status = request.data.get('status')
            
            item = OrderItem.objects.filter(tracking_number=tracking_number).first()
            if item and status == 'delivered':
                  send_notification_and_email(
                        user=item.order.user,
                        subject = "Your Order Has Been Delivered!",
                        message = f"Your product '{item.product.name}' has been delivered successfully.",
                        notification_type = "email"
                  )
            return Response({'message':'Done'},status=200)