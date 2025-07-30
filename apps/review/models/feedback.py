from django.conf import settings
from django.db import models

from apps.recommendation.models import Recommendation


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedbacks")
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE, related_name="feedbacks")
    satisfaction_score = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user} on {self.recommendation.id}"
