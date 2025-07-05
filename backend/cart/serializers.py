from .models import CartItem
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


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
            
      def validate(self, data):
            product = data.get('product') or getattr(self.instance, 'product', None)
            quantity = data.get('quantity') or getattr(self.instance, 'quantity', None)
            
            if product is None:
                  raise ValidationError('Product must be set')
            
            if quantity is None:
                  quantity = 1
            
            if product.stock == 0:
                  raise ValidationError('This product is out of stock')
            if product.stock < quantity:
                  raise ValidationError(f"Only {data['product'].stock} left in stock, but you requested {data['quantity']}.")
            
            return data