from rest_framework import serializers

from apps.review.models import Review


class ReviewSummaryReviewSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user_id", "content", "rating", "created_at"]


class ReviewSummarySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    average_rating = serializers.FloatField()
    review_count = serializers.IntegerField()
    latest_reviews = ReviewSummaryReviewSerializer(many=True)
