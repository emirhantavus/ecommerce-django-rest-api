from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer
from .models import Notification

class NotificationListAPIView(APIView):
      permission_classes = [IsAuthenticated]
      
      def get(self,request):
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
            serializer = NotificationSerializer(notifications, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)