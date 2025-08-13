import uuid

from django.db import models

from apps.product.models import Product


class Product_Exchange(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="exchanges")
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_img_url = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class ExchangeReturnRequest(models.Model):
    REQUEST_TYPE_CHOICES = (
        ("exchange", "교환"),
        ("return", "반품"),
    )
    STATUS_CHOICES = (
        ("pending", "대기"),
        ("processing", "처리중"),
        ("completed", "승인 완료"),
        ("rejected", "승인 거절"),
    )

    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # order_id가 주문 모델 FK이면 이렇게:
    # order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    requests_at = models.DateTimeField(null=True, blank=True)
    exchange_return = models.CharField(max_length=100, null=True, blank=True)
    requests_reason = models.CharField(max_length=100, null=True, blank=True)
    is_exchange_available = models.BooleanField(default=True)
    is_return_available = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.get_type_display()} - {self.get_status_display()}]"
