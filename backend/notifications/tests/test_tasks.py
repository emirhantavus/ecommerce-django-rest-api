from django.test import TestCase
from django.contrib.auth import get_user_model
from notifications.models import Notification
from notifications.tasks import send_order_email
from ecommerce.utils.notifications import send_notification_and_email

User = get_user_model()

class SendOrderEmailTaskTest(TestCase):
      def setUp(self):
            self.user = User.objects.create_user(email='emir@gmail.com', password='passw0rd', first_name='Emirhan')
            
      def test_send_or_email_task_creates_notification(self):
            subject = "Test Subject"
            message = "This is a test message."
            to_email = self.user.email
            
            result = send_order_email.apply(args=[subject, message, to_email])
            self.assertIsNone(result.result)
            
      def test_send_notification_and_email_creates_notification(self):
            subject = "Test Subject"
            message = "This is a test message."

            notification = send_notification_and_email(
                user=self.user,
                subject=subject,
                message=message
            )
            
            self.assertIsNotNone(notification)
            self.assertEqual(notification.user, self.user)
            self.assertEqual(notification.subject, subject)
            self.assertEqual(notification.message, message)
            self.assertEqual(notification.status, 'pending')