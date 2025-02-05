from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
      
      CUSTOMER = "customer"
      SELLER = "seller"
      ADMIN = "admin"   
      
      ROLE_CHOICES = [
          (CUSTOMER, "Customer"),
          (SELLER, "Seller"),
          (ADMIN, "Admin"),
      ]     
      
      
      email = models.EmailField(unique=True)
      phone_number = models.CharField(max_length=15, blank=True, null=True)
      date_of_birth = models.DateField(blank=True, null=True)
      profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)     
      
      country = models.CharField(max_length=100, blank=True, null=True)
      city = models.CharField(max_length=100, blank=True, null=True)
      address = models.TextField(blank=True, null=True)
      postal_code = models.CharField(max_length=10, blank=True, null=True)    
      
      role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CUSTOMER)      
      
      is_active = models.BooleanField(default=True)
      is_staff = models.BooleanField(default=False)   
      USERNAME_FIELD = 'email'
      REQUIRED_FIELDS = []    
      
      objects = CustomUserManager() 
      
      def __str__(self):
          return f"{self.email} ({self.role})"
