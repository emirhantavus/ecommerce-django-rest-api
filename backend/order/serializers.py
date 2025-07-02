from rest_framework import serializers
from .models import Order, OrderItem


class OrderSerializer(serializers.ModelSerializer):
      user_email = serializers.CharField(source='user.email',read_only=True)
      class Meta:
            model = Order
            fields = ('id','user_email','status','address','created_at','total_price')
            
            
class OrderItemSerializer(serializers.ModelSerializer):
      product_name = serializers.CharField(source='product.name',read_only=True)
      class Meta:
            model = OrderItem
            fields = ('id','product_name','quantity','price')
            
class PostOrderAndItemSerializer(serializers.ModelSerializer):
      orderItems = OrderItemSerializer(many=True, write_only=True)
      
      class Meta:
            model = Order
            fields = ('user_email','status','address','created_at','total_price','orderItems')
            
      def create(self, validated_data):
            items = validated_data.pop('orderItems')
            order = Order.objects.create(**validated_data) #total_price veya user da sıkıntı olabilir bakmam lazım sonra.!!
            for item in items: #####UNUTMA
                  OrderItem.objects.create(order=order, **item)
            return order 