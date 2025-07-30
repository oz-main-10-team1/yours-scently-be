from django.conf import settings
from django.db import models

from apps.product.models import Perfume


class Recommendation(models.Model):
    class Type(models.TextChoices):
        AI = "ai", "AI 기반"
        SURVEY = "survey", "설문 기반"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    perfume = models.ForeignKey(
        Perfume,
        on_delete=models.CASCADE,
    )
    similarity_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
    )
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
    )
    context = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recommendation"
