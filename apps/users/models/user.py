from datetime import date

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from apps.users.manager.user_manager import CustomUserManager


class User(AbstractBaseUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "관리자"
        GENERAL = "GENERAL", "일반회원"

    class Gender(models.TextChoices):
        MALE = "MALE", "남성"
        FEMALE = "FEMALE", "여성"

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=30)
    nickname = models.CharField(max_length=10, unique=True)
    gender = models.CharField(max_length=6, choices=Gender.choices, default=Gender.MALE)
    birth_date = models.DateField(default=date(2000, 1, 1))
    phone_number = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.GENERAL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    class Meta:
        db_table = "users"
