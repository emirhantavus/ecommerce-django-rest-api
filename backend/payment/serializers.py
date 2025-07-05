from rest_framework import serializers
from .models import Payment
from order.models import Order
from rest_framework.exceptions import PermissionDenied, ValidationError

class PaymentSerializer(serializers.ModelSerializer):
      class Meta:
            model = Payment
            fields = ('id','user','order','status','transaction_id','created_at')
            read_only_fields = ('user','amount', 'transaction_id','created_at')
            
      def validate(self, data):
            for item in data['order'].order_items.all():
                  if item.product.stock < item.quantity:
                        raise ValidationError(f"Not enough stock for {item.product.name} ")
            return data 
                              
      def validate_transaction_id(self, obj):
            if Payment.objects.filter(transaction_id=obj).exists():
                  raise serializers.ValidationError('Transaction ID already exists')
            return obj
            
      def create(self, validated_data):
            user = self.context['request'].user
            order = validated_data['order']
            if isinstance(order, Order):
                  order_id = order.id
            else:
                  order_id = order
            order = Order.objects.get(id=order_id)
            amount = order.total_price
            
            ## For testing, I want to change status (T,F) random
            import random
            status = random.choice([True,False])
            ##Also transaction_id with using uuid
            import uuid
            transaction_id = str(uuid.uuid4())
            
            if order.user != self.context['request'].user:
                  raise PermissionDenied('You can only pay for your own orders.')
            
            payment = Payment.objects.create(
                  user=user,
                  amount=amount,
                  status=status,
                  transaction_id=transaction_id,
                  order=order
                  )
            
            ## we change order's status here and product's stock info
            if status:
                  payment.order.status = 'paid'
                  for item in payment.order.order_items.all():
                       item.product.stock -= item.quantity
                       item.product.save()
                  
            else:
                  payment.order.status = 'failed'
            payment.order.save()
            
            return payment