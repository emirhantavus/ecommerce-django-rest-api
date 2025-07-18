from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from order.models import Order, OrderItem
from .serializers import PaymentSerializer
from .models import Payment
from order.permissions import IsCustomer, IsSellerOrAdmin
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()

class PaymentAPIView(APIView):
      permission_classes = [IsAuthenticated]
      
      @swagger_auto_schema(request_body=PaymentSerializer)
      def post(self,request):
            serializer = PaymentSerializer(data=request.data, context={'request':request})
            if serializer.is_valid():
                  payment = serializer.save()
                  return Response({
                        'payment_id': payment.id,
                        'amount': str(payment.amount),
                        'status': payment.status,
                        'transaction_id': payment.transaction_id
                        }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
      
      def get(self, request):
            payments = Payment.objects.filter(user=request.user).order_by('-created_at')
            serializer = PaymentSerializer(payments, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
      
      
class PaymentListCustomerAPIView(APIView):
      permission_classes = [IsCustomer]
      
      def get(self, request):
            payments = Payment.objects.filter(user=request.user,status=True).order_by('-created_at')
            pyms = []
            for pay in payments:
                  items = []
                  for item in pay.order.order_items.all():
                        items.append({
                              "product_name":item.product.name,
                              "quantity":item.quantity,
                              "unit_price":item.price
                        })
                        
                  pyms.append({
                        "paymend_id":pay.id,
                        "order_id":pay.order.id,
                        "total_paid":pay.order.total_price,
                        "created_at":pay.created_at,
                        "items":items
                  })
            return Response({'payments':pyms},status=status.HTTP_200_OK)
      
      
class SellerSalesListAPIView(APIView):
      permission_classes = [IsSellerOrAdmin]
      
      def get(self, request):
            items = OrderItem.objects.filter(product__seller=request.user, order__status='delivered')
            total_earnings=0
            sales = [] #I can change this maybe I write a mini serializer for this view
            
            for item in items:
                  total_earnings += item.quantity * item.price
                  
                  sales.append({
                        "product_name":item.product.name,
                        "quantity":item.quantity,
                        "total":item.quantity * item.price,
                        "order_id":item.order.id,
                        "order_date":item.order.created_at,
                        "buyer_email":item.order.user.email,
                  })
                  
            return Response({
                  "total_earnings":total_earnings,
                  "sales":sales
            },status=200)