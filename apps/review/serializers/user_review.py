from rest_framework import serializers

from apps.review.models import Review


class UserReviewItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    review_id = serializers.IntegerField(source="id", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", read_only=True)

    class Meta:
        model = Review
        fields = (
            "review_id",
            "product_id",
            "product_name",
            "content",
            "rating",
            "created_at",
        )


class UserReviewListSerializer(serializers.Serializer):
    reviews = UserReviewItemSerializer(many=True)
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    total = serializers.IntegerField()
