from rest_framework import serializers
from .models import Order, OrderItem
from cart.models import CartItem
from order.services.shipment_service import get_shipment_by_tracking_number
from django.db import transaction
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models import Prefetch


class OrderItemSerializer(serializers.ModelSerializer):
      product_name = serializers.CharField(source='product.name',read_only=True)
      shipment = serializers.SerializerMethodField()
      class Meta:
            model = OrderItem
            fields = ('id','product_name','quantity','price','shipment')
            
      def get_shipment(self,obj):
            if obj.tracking_number:
                  return get_shipment_by_tracking_number(obj.tracking_number)
            return None

class OrderSerializer(serializers.ModelSerializer):
      items = OrderItemSerializer(many=True, read_only=True, source='order_items')
      class Meta:
            model = Order
            fields = ('id','status','address','created_at','total_price','items')
            read_only_fields = ('id', 'created_at', 'total_price','status')
            
      def create(self, validated_data):
            user = self.context['request'].user
            cart_items = CartItem.objects.filter(user=user).select_related('product')
            items = list(cart_items)
            if not items:
                  raise serializers.ValidationError('cart is empty')
            
            with transaction.atomic():
                  order = Order.objects.create(
                        user=user,
                        address=validated_data['address'],
                        total_price=Decimal('0.00')
                  )
                  order_items_rows = []
                  total = Decimal('0.00')
                  
                  for ci in items:
                        price = ci.product.discount_price
                        if price is None:
                              raise ValidationError('Product has no price.')
                        if ci.quantity<=0:
                              raise ValidationError('Cart item quanity must greater than 0')
                        
                        order_items_rows.append(
                              OrderItem(
                                    order=order,
                                    product=ci.product,
                                    quantity=ci.quantity,
                                    price=price,
                              )
                        )
                        total += Decimal(price) * ci.quantity
                  
                  OrderItem.objects.bulk_create(order_items_rows, batch_size=1000)
                  
                  Order.objects.filter(pk=order.pk).update(total_price=total)
                  order.total_price = total

                  CartItem.objects.filter(user=user).delete()
                  
                  order = (
                        Order.objects.filter(pk=order.pk).prefetch_related(
                              Prefetch(
                                    'order_items',
                                    queryset=OrderItem.objects.select_related('product')
                                    )
                              )
                        .get()
                  )
                  '''
                        With order prefetch_related, we solve product-orderitems N+1 problem but maybe no need it.
                        Actually we won't order +100 items. It increase ms time for low quantity orders.
                        But no big difference. But better to use it for wholesalers..
                  '''
            return order
            
class ReturnRequestSerializer(serializers.ModelSerializer):
      class Meta:
            model = OrderItem
            fields = ('id','return_type','return_reason','return_image')
            extra_kwargs = {
                  'return_type': {'required':True},
                  'return_reason': {'required':True},
                  'return_image': {'required':False}
            }
            
            
class OrderHistoryCustomerSerializer(serializers.ModelSerializer):
      items = OrderItemSerializer(many=True, read_only=True, source='order_items')
      class Meta:
            model = Order
            fields = ('id','address','created_at','total_price','items')
            read_only_fields = ('id', 'created_at', 'total_price','status')
            
            
class OrderHistorySellerSerializer(serializers.ModelSerializer):
      buyer = serializers.SerializerMethodField()
      order_id = serializers.IntegerField(source='order.id', read_only=True)
      order_status = serializers.CharField(source='order.status', read_only=True)
      order_date = serializers.DateTimeField(source='order.created_at', read_only=True)
      product_name = serializers.CharField(source='product.name', read_only=True)
      product_price = serializers.DecimalField(source='price', read_only=True, max_digits=10, decimal_places=2)
      item_total_price = serializers.SerializerMethodField()
      
      class Meta:
            model = OrderItem
            fields = (
                  'id','order_id','order_date','order_status','product_name','product_price','quantity','item_total_price','buyer'
                  )
            
      def get_buyer(self,data):
            user = data.order.user
            return {
                  'id':user.id,
                  'name':f"{user.first_name} {user.last_name}",
                  'email':user.email
            }
      
      def get_item_total_price(self,data):
            return data.quantity * data.price