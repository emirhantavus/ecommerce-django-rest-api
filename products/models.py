from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
      name = models.CharField(max_length=255, unique=True)
      parent = models.ForeignKey(
            "self", on_delete=models.CASCADE, null=True,blank=True,related_name='subcategories'
      )
      level = models.IntegerField(default=0)
      
      class Meta:
            verbose_name_plural = "Categories"
            
      def save(self, *args, **kwargs):
            if self.parent:
                  self.level = self.parent.level + 1
            else:
                  self.level = 0
            super().save(*args,**kwargs)
      
      def __str__(self):
            return f"Category name: {self.name}"
      

class Product(models.Model):
      name = models.CharField(max_length=255)
      description = models.TextField()
      price = models.DecimalField(max_digits=10, decimal_places=2)
      stock = models.PositiveIntegerField(null=False)
      category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)
      seller = models.ForeignKey(User,on_delete=models.CASCADE, related_name='products')
      image = models.ImageField(upload_to='products/')
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)
      active = models.BooleanField(default=True)
      discount = models.BooleanField(default=False)
      discount_rate = models.IntegerField(default=0)
      
      class Meta:
            ordering = ["-created_at"]
            
      def save(self, *args, **kwargs):
            if self.stock == 0:
                  self.active = False
            super().save(*args,**kwargs)
      
      @property
      def discount_price(self):
            if self.discount:
                  return self.price * (1 - self.discount_rate/100) #discounted price
            return self.price # normal price If there is not discount
            
      def __str__(self):
            return f"Product name: {self.name}"
      
class Favorites(models.Model):
      user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='favorites')
      product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
      created_at = models.DateTimeField(auto_now_add=True)
      
      class Meta:
            unique_together = ('user','product')
            
      def __str__(self):
            return f"{self.user.mail} -- {self.product.name}"