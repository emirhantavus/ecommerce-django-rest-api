from notifications.tasks import send_order_email
from notifications.models import Notification
import logging

def send_notification_and_email(user, subject, message, status='pending',notification_type='email'):
      try:
            result = send_order_email.delay(subject=subject,message=message,user=user.email)
            task_id = result.id

            notification = Notification.objects.create(
                  user=user,
                  notification_type=notification_type,
                  subject=subject,
                  message=message,
                  status=status,
                  task_id=task_id
            )
            return notification
      except Exception as e:
            logging.error(f"Notification send failed: {e}")
            
            try:
                  Notification.objects.create(
                        user=user,
                        notification_type=notification_type,
                        subject=subject,
                        message=message,
                        status='failed',
                        task_id=None,
                        error_msg=str(e)
                  )
            except Exception as ex:
                  logging.critical(f"Notification DB log failed: {ex}")