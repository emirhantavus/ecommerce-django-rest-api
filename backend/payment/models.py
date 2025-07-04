from django.db import models
from django.contrib.auth import get_user_model
from order.models import Order

User = get_user_model()

class Payment(models.Model):
      user = models.ForeignKey(User,on_delete=models.CASCADE)
      order = models.ForeignKey(Order, on_delete=models.CASCADE)
      amount = models.DecimalField(max_digits=10, decimal_places=2)
      transaction_id = models.CharField(max_length=255,null=True, blank=True, unique=True)
      status = models.BooleanField(default=False)
      created_at = models.DateTimeField(auto_now_add=True)
      
      def __str__(self):
            return f"{self.user.email} -- {self.order.id} -- {self.status}"