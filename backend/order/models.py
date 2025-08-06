from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from cart.models import CartItem

User = get_user_model()

class Order(models.Model):
      STATUS_CHOICES = [
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('cancelled', 'Cancelled'),
            ('failed','Failed'),
            #### for refund product or products.
            ('return_requested','Return Requested'),
            ('returned', 'Returned'),
            ('refund_rejected', 'Refund Rejected'),
      ]
      user = models.ForeignKey(User, on_delete=models.CASCADE)
      address = models.CharField(max_length=512, null=False)
      status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='pending')
      created_at = models.DateTimeField(auto_now_add=True)
      total_price = models.DecimalField(max_digits=10, decimal_places=2)
      
      def __str__(self):
            return f"{self.user} -- {self.total_price} -- {self.status} -- {self.created_at}"

class OrderItem(models.Model):
      order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='order_items')
      product = models.ForeignKey(Product, on_delete=models.PROTECT)
      quantity = models.PositiveIntegerField()
      price = models.DecimalField(max_digits=10, decimal_places=2)
      
      tracking_number = models.CharField(max_length=100, blank=True, null=True) #Shipment
      
      RETURN_STATUS_CHOICES = [
            ('none', 'No Return'),
            ('requested', 'Return Requested'),
            ('approved', 'Return Approved'),
            ('rejected', 'Return Rejected'),
            ('completed', 'Return Completed'),
      ]
      RETURN_TYPE_CHOICES = [
            ('refund', 'Refund'),
            ('exchange', 'Exchange'),
      ]
      
      return_status = models.CharField(max_length=30, choices=RETURN_STATUS_CHOICES,default='none')
      return_type = models.CharField(max_length=20, choices=RETURN_TYPE_CHOICES, blank=True, null=True)
      return_reason = models.TextField(max_length=1024,blank=True, null=True)
      return_image = models.ImageField(upload_to='returns/',blank=True, null=True) # maybe it's unnecessary
      
      def __str__(self):
            return f"{self.product.name} -- {self.quantity} -- {self.price} -- {self.return_status} -- {self.tracking_number}"