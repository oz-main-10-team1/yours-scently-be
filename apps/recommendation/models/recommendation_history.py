from django.db import models

from apps.product.models import Perfume
from apps.recommendation.models import Recommendation


class RecommendationHistory(models.Model):
    class RecommendationHistory(models.Model):
        recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE, related_name="histories")
        perfume = models.ForeignKey(Perfume, on_delete=models.PROTECT, related_name="recommendation_histories")
        similarity_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
        created_at = models.DateTimeField(auto_now_add=True)

        class Meta:
            db_table = "recommendation_history"
            ordering = ["-created_at"]

        def __str__(self):
            return f"Perfume {self.perfume} for Recommendation {self.recommendation.id}"
