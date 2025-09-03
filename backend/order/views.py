from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import (OrderSerializer, ReturnRequestSerializer,
                          OrderHistoryCustomerSerializer, OrderHistorySellerSerializer ,OrderItemSerializer,
                          SellerOrderItemSerializer)
from .permissions import IsCustomer, IsSellerOrAdmin
from django.shortcuts import get_object_or_404
from ecommerce.utils.notifications import send_notification_and_email
from drf_yasg.utils import swagger_auto_schema
from order.services.shipment_service import create_shipment
from django.db.models import Prefetch
from products.models import Product
from order.services.shipment_service import get_shipment_by_tracking_number
import requests

SHIPMENT_API_URL = "http://shipping-api:9000/api/shipments/"

class OrderAPIView(APIView):
      permission_classes = [IsAuthenticated]
      
      def get(self, request):
            order = Order.objects.filter(user=request.user, status='paid')
            serializer = OrderSerializer(order, many=True)
            return Response(serializer.data,status.HTTP_200_OK)
      
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
            item = get_object_or_404(OrderItem.objects.select_related('product','order','order__user'),id=item_id)
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
            
            items = order.order_items.select_related('product')
            products_to_update = []
            
            #update stock restore // N+1 problem
            for item in items:
                  item.product.stock += item.quantity
                  products_to_update.append(item.product)
            Product.objects.bulk_update(products_to_update,['stock'])
            
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
            item = (
                  OrderItem.objects.select_related('product__seller__profile','order__user').get(
                        id=item_id, order__user=request.user)
            )
            shipment = get_shipment_by_tracking_number(item.tracking_number)
            if not shipment or shipment.get('status') != 'delivered':
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
                  
            serializer = ReturnRequestSerializer(items, many=True)#serializer kısmını sonra genisleticez unutma.
            return Response(serializer.data,status=200)
      
class ListReturnRequestsSellerAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      def get(self, request):
            status_param = request.query_params.get('status')
            items = OrderItem.objects.filter(product__seller=request.user).exclude(return_status='none')
            
            if status_param:
                  items = items.filter(return_status=status_param)
            serializer = ReturnRequestSerializer(items, many=True)
            return Response(serializer.data,status=200)
      
class ProcessReturnRequestsSellerAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      @swagger_auto_schema(request_body=None)
      def post(self,request,item_id):
            item = (
                  OrderItem.objects.select_related('product','order__user')
                  .filter(id=item_id,product__seller=request.user,return_status='requested')
                  .first()
            )
            if not item:
                  return Response({'message':'OrderItem not found'},status=400)
            
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
            orders = (Order.objects.filter(user=request.user,status__in=['delivered','cancelled'])
                      .prefetch_related(Prefetch('order_items',queryset=OrderItem.objects.select_related('product')))
                      .select_related('user'))
            serializer = OrderHistoryCustomerSerializer(orders,many=True)
            return Response(serializer.data,status=200)
      
      
class OrderHistoryDetailAPIView(APIView):
      permission_classes = [IsCustomer]
      
      def get(self,request,o_id):
            order = get_object_or_404(Order.objects.prefetch_related(
                  Prefetch('order_items',queryset=OrderItem.objects.select_related('product')))
                  .select_related('user'),
                  user=request.user,
                  id=o_id)
            serializer = OrderHistoryCustomerSerializer(order)
            return Response(serializer.data,status=200)
      
class OrderHistorySellerAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      def get(self,request):
            items = (OrderItem.objects.filter(product__seller=request.user).select_related('order__user','product')
                     .order_by('-id'))
            tracking_numbers = [i.tracking_number for i in items if i.tracking_number]
            if not tracking_numbers:
                  return Response([],status=200)
            
            resp = requests.post(
                  f"{SHIPMENT_API_URL}get-status/",
                  json={'tracking_numbers':tracking_numbers},
                  timeout=5
            )
            shipment_status = resp.json()
            delivered_items = [item for item in items if shipment_status.get(item.tracking_number) == 'delivered']
            serializer = OrderHistorySellerSerializer(delivered_items, many=True,context={'shipment_status':shipment_status})
            return Response(serializer.data,status=200)
      
class ActiveOrderListAPIView(APIView):
      permission_classes = [IsCustomer]
      
      def get(self,request):
            orders = (
                  Order.objects.filter(
                  user=request.user,
                  status__in=['pending','paid','shipped']
            )
                      .order_by('-created_at')
                      .prefetch_related(
                            Prefetch( 
                              'order_items',
                              queryset=OrderItem.objects.select_related('product')
                            )
                        )
            )
            '''
                  200 GET
                  /api/order/active/
                  195ms overall
                  40ms on queries
                  34 queries
                  
                  TO
                  
                  200 GET
                  /api/order/active/
                  40ms overall
                  8ms on queries
                  3 queries
            '''
            serializer = OrderHistoryCustomerSerializer(orders,many=True)
            return Response(serializer.data,status=200)
      
      
class SellerOrderItemsNotShippedAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      def get(self,request):
            items = OrderItem.objects.filter(
                  product__seller=request.user,
                  order__status='paid',
                  tracking_number__isnull=True
                  ).order_by('-order__created_at').select_related('product','order__user')
            serializer = SellerOrderItemSerializer(items,many=True)
            return Response(serializer.data,status=200)
      
class SellerCancelledItemsAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      def get(self,request):
            items = OrderItem.objects.filter(
                  product__seller=request.user, order__status='cancelled').select_related('product','order')
            serializer = OrderItemSerializer(items, many=True)
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