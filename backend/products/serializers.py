from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Product, Category , Favorites
from decimal import Decimal
from django.db.models import Avg

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
      subcategories = serializers.SerializerMethodField()
      class Meta:
            model = Category
            fields = ('id','name','level','subcategories')
            
      def get_subcategories(self,obj):
            return CategorySerializer(obj.subcategories.all(), many=True).data
      
class SellerSerializer(serializers.ModelSerializer):
      class Meta:
            model = User
            fields = ('id','email','phone_number')############
      
      
class SimpleProductSerializer(serializers.ModelSerializer):
      class Meta:
            model = Product
            fields = ('id','name','price','stock')
            
            
class ProductSerializer(serializers.ModelSerializer):
      discounted_price = serializers.SerializerMethodField()
      low_stock = serializers.SerializerMethodField()
      seller = SellerSerializer(read_only=True)
      price = serializers.DecimalField(max_digits=10,decimal_places=2,coerce_to_string=False)
      is_favorited = serializers.SerializerMethodField()
      average_rating = serializers.SerializerMethodField()
      review_count = serializers.SerializerMethodField()
      class Meta:
            model = Product
            fields = ('id','name','price','discount','discounted_price','discount_rate','stock',
                      'active','low_stock','category','is_favorited','seller','average_rating',
                      'review_count')
            
      def create(self, validated_data):
            validated_data['seller'] = self.context['request'].user
            return super().create(validated_data)
            
      
      def get_discounted_price(self,obj):
            price = Decimal(obj.price) if isinstance(obj.price, float) else obj.price
            discount_rate = Decimal(obj.discount_rate) if isinstance(obj.discount_rate, float) else obj.discount_rate
            if obj.discount and obj.discount_rate > 0:
                  return round(price * (1 - discount_rate / Decimal(100)), 2)
            return None
            
      def get_low_stock(self, obj):
            if obj.stock <= 5:
                  return {"low_stock":True}
            return {"low_stock":False}
      
      def get_is_favorited(self, obj):
            request = self.context.get('request',None)
            if not request or not  request.user.is_authenticated:
                  return False
            return Favorites.objects.filter(user=request.user, product_id=obj.id).exists()
      
      def get_average_rating(self, obj):
            average = obj.reviews.all().aggregate(Avg('rating'))
            average = average['rating__avg']
            if average is None:
                  return 0
            return round(average)
      
      def get_review_count(self,obj):
            return obj.reviews.all().count()
      

class FavoritesSerializer(serializers.ModelSerializer):
      product = ProductSerializer(read_only=True)
      
      class Meta:
            model = Favorites
            fields = ('id','product')