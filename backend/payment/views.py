from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from order.models import Order
from .serializers import PaymentSerializer
from .models import Payment

User = get_user_model()

class PaymentAPIView(APIView):
      permission_classes = [IsAuthenticated]
      
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