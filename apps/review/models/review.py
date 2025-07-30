from django.conf import settings
from django.db import models


class Perfume(models.Model):
    name = models.CharField(max_length=100)


class Review(models.Model):
    # 리뷰 작성자
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")

    # 어떤 향수에 대한 리뷰?
    perfume = models.ForeignKey(Perfume, on_delete=models.CASCADE, related_name="reviews")

    # 리뷰 내용
    content = models.TextField()

    # 생성 일시 / 수정 일시
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.perfume.name} 리뷰"
