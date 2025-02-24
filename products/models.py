from django.db import models
from django.contrib.auth import get_user_model

user = get_user_model()

class Category(models.Model):
      name = models.CharField(max_length=255, unique=True)
      parent = models.ForeignKey(
            "self", on_delete=models.CASCADE, null=True,blank=True,related_name='subcategories'
      )
      
      class Meta:
            verbose_name_plural = "Categories"
      
      def __str__(self):
            return f"Category name: {self.name}"
      

class Product(models.Model):
      name = models.CharField(max_length=255)
      description = models.TextField()
      price = models.DecimalField(max_digits=10, decimal_places=2)
      stock = models.PositiveIntegerField(default=0)
      category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)
      seller = models.ForeignKey(user,on_delete=models.CASCADE)
      image = models.ImageField(upload_to='products/')
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now_add=True)
      active = models.BooleanField(default=True)
      
      class Meta:
            ordering = ["-created_at"]
            
      def __str__(self):
            return f"Product name: {self.name}"