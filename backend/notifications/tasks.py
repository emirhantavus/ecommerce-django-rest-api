from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from notifications.models import Notification

@shared_task(bind=True, max_retries=5)
def send_order_email(self, subject, message, to_email,notification_id=None):
      try:
            send_mail(
                  subject,
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  [to_email]
            )
            if notification_id:
                  Notification.objects.filter(id=notification_id).update(status='delivered')
      except Exception as e:
            if notification_id:
                  Notification.objects.filter(id=notification_id).update(
                        status="failed",
                        error_msg=str(e)
                  )
                  raise self.retry(exc=e,countdown=60, max_retries=5)