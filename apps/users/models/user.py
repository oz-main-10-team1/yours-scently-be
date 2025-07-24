from datetime import date

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from apps.users.manager.user_manager import CustomUserManager

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=130)
    name = models.CharField(max_length=30, null=False, blank=False)
    nickname = models.CharField(max_length=10, unique=True, null=False, blank=False)
    birth_date = models.DateField(default=date(2000, 1, 1), null=False, blank=False)
    phone_number = models.CharField(max_length=20, unique=True, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    class Meta:
        db_table = "users"