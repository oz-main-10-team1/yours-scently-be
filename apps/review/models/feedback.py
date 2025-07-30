from django.conf import settings
from django.db import models

from .review import Review


class Feedback(models.Model):
    # 피드백 작성자
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedbacks")

    # 어떤 리뷰에 대한 피드백인지
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="feedbacks")

    # 도움이 되었는지 여부
    is_helpful = models.BooleanField()

    # 생성 일시
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user} on review {self.review.id} - Helpful: {self.is_helpful}"
