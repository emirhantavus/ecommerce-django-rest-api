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
            CartItem.objects.filter(user=user).delete()
            
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