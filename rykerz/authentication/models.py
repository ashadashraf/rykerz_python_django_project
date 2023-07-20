from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager

# Create your models here.

class CustomUser(AbstractUser):
    username = None
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    mobile = models.TextField(max_length=20)
    password = models.CharField(max_length=100)
    is_user = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','password']

    objects = CustomUserManager()

    def __str__(self):
        return "{}".format(self.email)