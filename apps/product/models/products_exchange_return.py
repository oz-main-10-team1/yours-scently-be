import uuid

from django.db import models

from apps.product.models import Product


class ProductExchange(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="exchanges",
    )

    # 테스트에서 필요한 필드 추가
    is_exchange_available = models.BooleanField(default=True)
    is_return_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ExchangeReturnRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ("exchange", "Exchange"),
        ("return", "Return"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, choices=REQUEST_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    exchange_return = models.ForeignKey("ProductExchange", on_delete=models.SET_NULL, null=True, blank=True)
    requests_reason = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type} request for {self.exchange_return.name}"
