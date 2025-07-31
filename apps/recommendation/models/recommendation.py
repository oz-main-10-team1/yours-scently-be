from django.conf import settings
from django.db import models

from apps.product.models import Perfume


class Recommendation(models.Model):
    class Type(models.TextChoices):
        AI = "ai", "AI 기반"
        SURVEY = "survey", "설문 기반"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recommendations")
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
    )
    context = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recommendation"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.type}] Recommendation by {self.user} at {self.created_at}"
