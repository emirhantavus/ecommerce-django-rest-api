from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
      user = serializers.SerializerMethodField()
      product = serializers.SerializerMethodField()
      class Meta:
            fields = ('id','user','product','rating','comment','created_at')
            
      def get_user(self,obj):
            return {
                  "id":obj.user.id,
                  "email":obj.user.email
            }
            
      def get_product(self,obj):
            return{
                  "id":obj.product.id,
                  "name":obj.product.name
            }
            
      def create(self, validated_data):
            user = self.context['request'].user
            product = self.context['product']
            return Review.objects.create(user=user,product=product,**validated_data)