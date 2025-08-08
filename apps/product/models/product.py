from django.db import models

from apps.product.models.perfume import Perfume  # perfume 모델 import


class Product(models.Model):
    class Category(models.TextChoices):
        DAILY = "Daily", "데일리"
        SPECIAL = "Special", "특별한 날"
        RELAX = "Relax", "휴식 및 기분전환"
        OUTDOOR = "Outdoor", "운동 및 야외 활동"

    perfume = models.ForeignKey(
        Perfume,
        on_delete=models.CASCADE,
        related_name="products",
        null=False,
        blank=False,
    )
    volume_ml = models.PositiveIntegerField(default=50)

    name = models.CharField(max_length=100)  # 샤넬 100ml
    description = models.TextField()
    category = models.CharField(choices=Category.choices, max_length=10)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    stock = models.PositiveIntegerField()
    product_img_url = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "product"
