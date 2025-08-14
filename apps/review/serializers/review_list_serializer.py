from rest_framework import serializers

from apps.review.models import Review


class ReviewListSerializer(serializers.ModelSerializer):
    review_id = serializers.IntegerField(source="id")
    user_nickname = serializers.CharField(source="user.nickname")

    class Meta:
        model = Review
        fields = ["review_id", "user_nickname", "rating", "content", "created_at"]
