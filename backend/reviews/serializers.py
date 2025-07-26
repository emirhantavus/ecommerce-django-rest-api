from rest_framework import serializers
from .models import Review
from ecommerce.utils.notifications import send_notification_and_email

class ReviewSerializer(serializers.ModelSerializer):
      user = serializers.SerializerMethodField()
      product = serializers.SerializerMethodField()
      class Meta:
            model = Review
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
            send_notification_and_email(
                  user=product.seller,
                  subject=f"New review for your product {product.name}",
                  message=(
                        f"{user.email} has submitted a review for your product {product.name} \n"
                        f"Rating: {validated_data['rating']} \n"
                        f"Comment: {validated_data['comment']}"
                  )
            )
            return Review.objects.create(user=user,product=product,**validated_data)