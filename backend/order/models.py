from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from cart.models import CartItem

User = get_user_model()

class Order(models.Model):
      STATUS_CHOICES = [
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
      ]
      user = models.ForeignKey(User, on_delete=models.CASCADE)
      address = models.CharField(max_length=512, null=False)
      status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='pending')
      created_at = models.DateTimeField(auto_now_add=True)
      total_price = models.DecimalField(max_digits=10, decimal_places=2)
      
      def __str__(self):
            return f"{self.user} -- {self.total_price} -- {self.status} -- {self.created_at}"

class OrderItem(models.Model):
      order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='items')
      product = models.ForeignKey(Product, on_delete=models.PROTECT)
      quantity = models.PositiveIntegerField()
      price = models.DecimalField(max_digits=10, decimal_places=2)
      
      def __str__(self):
            return f"{self.product.name} -- {self.quantity} -- {self.price}"