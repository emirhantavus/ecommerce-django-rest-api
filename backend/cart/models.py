from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

###### Bad design for now, later I may add cart and cartItem models. It works now but, create cart everytime.

User = get_user_model()
class CartItem(models.Model):
      user = models.ForeignKey(User, on_delete=models.CASCADE,null=False,blank=False)
      product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)
      quantity = models.PositiveIntegerField(default=1)
      added_at = models.DateTimeField(auto_now_add=True)
      
      class Meta:
            unique_together = ('user','product')
      
      @property
      def get_total_price(self):
            if self.product.discount:
                  return self.product.discount_price * self.quantity
            return self.product.price * self.quantity
      
      def __str__(self):
            return f"{self.user.email} -- {self.product.name} -- {self.quantity}"
      