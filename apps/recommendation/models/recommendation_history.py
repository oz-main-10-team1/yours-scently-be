from django.db import models

from apps.product.models import Perfume
from apps.recommendation.models import Recommendation


class RecommendationHistory(models.Model):
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE, related_name="histories")
    perfume = models.ForeignKey(Perfume, on_delete=models.CASCADE, related_name="recommendation_histories")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recommendation_history"
        ordering = ["-created_at"]
