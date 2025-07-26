from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Review(models.Model):
      user = models.ForeignKey(User, on_delete=models.CASCADE)
      product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
      rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
      comment = models.TextField(blank=True)
      created_at = models.DateTimeField(auto_now_add=True)
      
      class Meta:
            unique_together = ('user','product')
            
      def __str__(self):
            return f"{self.user.email} -- {self.product.pk} -- {self.rating} -- {self.created_at}"