from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Product, Category

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
      subcategories = serializers.SerializerMethodField()
      class Meta:
            model = Category
            fields = ('id','name','level','subcategories')
            
      def get_subcategories(self,obj):
            return CategorySerializer(obj.subcategories.all(), many=True).data
      
      
class SimpleProductSerializer(serializers.ModelSerializer):
      class Meta:
            model = Product
            fields = ('id','name','price','stock')
            
            
class ProductSerializer(serializers.ModelSerializer):
      discounted_price = serializers.SerializerMethodField()
      low_stock = serializers.SerializerMethodField()
      class Meta:
            model = Product
            fields = ('id','name','price','stock','active','discounted_price','low_stock','category')
            
      def create(self, validated_data):
            validated_data['seller'] = self.context['request'].user
            return super().create(validated_data)
            
      
      def get_discounted_price(self,obj):
            if obj.discount and obj.discount_rate > 0:
                  return round(obj.price * (1 - obj.discount_rate / 100), 2)
            return obj.price
            
      def get_low_stock(self, obj):
            if obj.stock <= 5:
                  return {"low_stock":True}
            return {"low_stock":False}