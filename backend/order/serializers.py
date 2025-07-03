from rest_framework import serializers
from .models import Order, OrderItem
from cart.models import CartItem


class OrderItemSerializer(serializers.ModelSerializer):
      product_name = serializers.CharField(source='product.name',read_only=True)
      class Meta:
            model = OrderItem
            fields = ('id','product_name','quantity','price')

class OrderSerializer(serializers.ModelSerializer):
      items = OrderItemSerializer(many=True, read_only=True, source='order_items')
      class Meta:
            model = Order
            fields = ('id','status','address','created_at','total_price','items')
            read_only_fields = ('id', 'created_at', 'total_price','status')
            
      def create(self, validated_data):
            user = self.context['request'].user
            cart_items = CartItem.objects.filter(user=user)
            if not cart_items.exists():
                  raise serializers.ValidationError('cart is empty')
            
            order = Order.objects.create(user=user, address=validated_data['address'],total_price=0)
            total = 0 
            for cart_item in cart_items:
                  price = cart_item.product.discount_price
                  OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=price
                  )
            total += price * cart_item.quantity
            order.total_price = total
            order.save()
            
            #sepet temizlik burda kalsın simdilik
            cart_item.delete()
            
            return order
            