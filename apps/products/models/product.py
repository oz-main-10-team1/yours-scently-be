from django.db import models


class Product(models.Model):
    class Category(models.TextChoices):
        DAILY = "Daily", "데일리"
        SPECIAL = "Special", "특별한 날"
        RELAX = "Relax", "휴식 및 기분전환"
        OUTDOOR = "Outdoor", "운동 및 야외 활동"

    name = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    description = models.TextField()
    category = models.CharField(choices=Category.choices, max_length=10)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    stock = models.IntegerField()
    product_img_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product"
