from rest_framework import serializers
from .models import Payment
from order.models import Order
from rest_framework.exceptions import PermissionDenied, ValidationError
from ecommerce.utils.notifications import send_notification_and_email
from django.db.models import F , Prefetch
from order.models import OrderItem
from django.db import transaction
from products.models import Product

class PaymentSerializer(serializers.ModelSerializer):
      class Meta:
            model = Payment
            fields = ('id','user','order','amount','status','transaction_id','created_at')
            read_only_fields = ('user','amount', 'transaction_id','created_at')
            
      def validate(self, data):
            request = self.context.get('request')
            if not request or not request.user.is_authenticated:
                  raise ValidationError('Authentication required')
            
            order_obj = data.get('order')
            if isinstance(order_obj, Order):
                  order = order_obj
            else:
                  try:
                        order = Order.objects.only('id','user_id','status').get(pk=order_obj)
                  except Order.DoesNotExist:
                        raise ValidationError({'detail':'Order not found'})
            
            if order.user_id != request.user.id:
                  raise PermissionDenied('You can only pay for your own orders.')
            
            if Payment.objects.filter(order_id = order.id).exists():
                  raise ValidationError({'detail':'Payment already exists for this order.'})
            
            if getattr(order, 'status', None) != 'pending':
                  raise ValidationError({'detail':'Order status must be ,.pending.,'})
            
            items = (
                  order.order_items.filter(product__stock__lt=F('quantity')).select_related('product')
            )
            if items.exists():
                  names = sorted(set(items.values_list('product__name',flat=True)))
                  raise ValidationError({'detail':f"Not enough stock for:  {names}"})
            
            data['order'] = order
            return data
                  
            
      def create(self, validated_data):
            user = self.context['request'].user
            order = validated_data['order']
            amount = order.total_price
            ## For testing, I want to change status (T,F) random
            import random
            status = random.choice([True]) #ONLY TRUE FOR TESTING .!!
            ##Also transaction_id with using uuid
            import uuid
            transaction_id = str(uuid.uuid4())
            
            items = list(order.order_items.select_related('product','product__seller').all())
            
            with transaction.atomic():
                  product_ids=set()
                  for it in items:
                        product_ids.add(it.product_id)
                  
                  locked_list = (
                        Product.objects.select_for_update().filter(id__in=product_ids)
                  )
                  
                  def find_locked_products(p_id):
                        for p in locked_list:
                              if p.id == p_id:
                                    return p
                        return None
                  
                  insufficent_names = []
                  for it in items:
                        locked_product = find_locked_products(it.product_id)
                        if locked_product is None:
                              print('error')
                        else:
                              if locked_product.stock < it.quantity:
                                    insufficent_names.append(locked_product.name)
                        
                  if len(insufficent_names) > 0:
                        unique_names = set(insufficent_names)
                        names_text = ", ".join(unique_names)
                        raise ValidationError({'detail':F"Not enough stock for {names_text}"})
                  
                  payment = Payment.objects.create(
                        user=user,
                        amount=amount,
                        order=order,
                        transaction_id=transaction_id,
                        status=status
                  )
                  
                  if status:
                        order.status = 'paid'
                        
                        for it in items:
                              locked_product = find_locked_products(it.product_id)
                              if locked_product:
                                    locked_product.stock -= it.quantity
                                    
                        Product.objects.bulk_update(locked_list, ['stock'])
                        
                        def after_commit_success():
                              #For customer
                              send_notification_and_email(
                                    user=payment.order.user,
                                    subject='Your Order Has Been Recieved!',
                                    message=(
                                          f"Dear {payment.order.user.first_name},\n\n"
                                          f"Your order (ID: {payment.order.id}) has been successfuly placed."
                                          "You can track your order status on your profile.\n\n"
                                          "Thank you for shopping with us."
                                    ),
                                    notification_type='email'
                              )
            
                              ## For sellers
                              for it in items:
                                    send_notification_and_email(
                                          user=it.product.seller,
                                          subject="New Order Received!",
                                          message= (
                                                f"You have recieved a new order for your product '{it.product.name}' \n\n"
                                                f"(Quantity: {it.quantity}). \n\n"
                                                f"Please check your seller panel for details."
                                          ),
                                          notification_type='email'
                                    )
                        transaction.on_commit(after_commit_success)
                  else:
                        order.status = 'failed'
                        
                        def after_commit_failed():
                              send_notification_and_email(
                                    user=order.user,
                                    subject='Your Order Has Failed',
                                    message=(
                                          'JUST FAILED FOR NOW'
                                    ),
                                    notification_type='email'
                              )
                        transaction.on_commit(after_commit_failed)
                  order.save(update_fields=['status'])
            return payment