from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
      password = serializers.CharField(write_only=True, required=True,validators=[validate_password])
      password2 = serializers.CharField(write_only=True, required=True)
      
      class Meta:
            model = User
            fields = ('email','password','password2','phone_number')
      
      def validate(self, attrs):
            if attrs['password'] != attrs['password2']:
                  raise serializers.ValidationError({'password':'passwords do not match !'})
            return attrs
      
      def create(self,validated_data):
            validated_data.pop('password2')
            user = User.objects.create_user(**validated_data)
            return user
      
class UserSerializer(serializers.ModelSerializer):
      class Meta:
            model = User
            fields = ('id','email','phone_number')
            
class ProfileSerializer(serializers.ModelSerializer):
      email = serializers.SerializerMethodField()
      role = serializers.SerializerMethodField()
      class Meta:
            model = Profile
            fields = ('email','role','seller_name','company_name')
            
      def get_email(self, obj):
            return obj.user.email
      
      def get_role(self, obj):
            return obj.user.role 
      
class PasswordResetSerializer(serializers.Serializer):
      email =serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
      email = serializers.EmailField()
      token = serializers.CharField()
      new_password = serializers.CharField(min_length=8, write_only=True)

class LoginSerializer(serializers.Serializer):
      email = serializers.EmailField()
      password = serializers.CharField()