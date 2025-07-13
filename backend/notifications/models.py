from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
      
      NOTIFICATION_CHOICES = [
            ('email','Email'),
            ('sms','SMS'),
      ]
      
      STATUS_CHOICES = [
            ('pending','Pending'),
            ('sent','Sent'),
            ('failed','Failed'),
      ]
      
      user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
      notification_type = models.CharField(choices=NOTIFICATION_CHOICES,default='email')
      subject = models.CharField(max_length=255,null=False)
      message = models.TextField()
      status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='pending')
      created_at = models.DateTimeField(auto_now_add=True)
      sent_at = models.DateTimeField(null=True, blank=True)
      error_msg = models.TextField(null=True,blank=True)
      
      task_id = models.CharField(max_length=64, unique=True) # for celery task id
      
      def __str__(self):
            return f"{self.user} -- {self.notification_type} -- {self.subject[:40]}"