from rest_framework import serializers
from .models import Payment
from order.models import Order

class PaymentSerializer(serializers.ModelSerializer):
      class Meta:
            model = Payment
            fields = ('id','user','order','status','transaction_id','created_at')
            read_only_fields = ('user','amount', 'transaction_id','created_at')
            
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
            
            payment = Payment.objects.create(
                  user=user,
                  amount=amount,
                  status=status,
                  transaction_id=transaction_id,
                  order=order
                  )
            
            return payment