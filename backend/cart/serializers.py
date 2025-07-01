from .models import CartItem
from rest_framework import serializers


class CartItemSerializer(serializers.ModelSerializer):
      total_price = serializers.ReadOnlyField(source='get_total_price')
      product_name = serializers.CharField(source='product.name', read_only=True)
      product_price = serializers.ReadOnlyField(source='product.discount_price')
      product_image = serializers.ImageField(source='product.image',read_only=True)
      product_stock = serializers.IntegerField(source='product.stock',read_only=True)
      
      class Meta:
            model = CartItem
            fields = ('id','product','product_name','product_price',
                      'product_stock','quantity','total_price',
                      'added_at','product_image'
                      )
            
            read_only_fields = [
            'id', 'product_name', 'product_price', 'product_stock',
            'total_price', 'added_at', 'product_image'
            ]