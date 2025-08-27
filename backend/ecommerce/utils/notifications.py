from notifications.tasks import send_order_email
from notifications.models import Notification
import logging

def send_notification_and_email(user, subject, message, status='pending',notification_type='email'):
      try:
            notification = Notification.objects.create(
                  user=user,
                  notification_type=notification_type,
                  subject=subject,
                  message=message,
                  status='pending'
            )
            
            result = send_order_email.delay(
                  subject=subject,
                  message=message,
                  to_email=user.email,
                  notification_id=notification.id
            )
            notification.task_id = result.id
            notification.save(update_fields=['task_id'])
            
            return notification
      except Exception as e:
            logging.error(f"Notification send failed: {e}")
            Notification.objects.create(
                  user=user,
                  notification_type=notification_type,
                  subject=subject,
                  message=message,
                  status='failed',
                  task_id=None,
                  error_msg=str(e)
            )