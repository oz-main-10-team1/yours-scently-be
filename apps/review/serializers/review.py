from rest_framework import serializers

from apps.review.models import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "product_id", "user_id", "content", "rating", "created_at"]

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("평점은 1에서 5 사이의 정수여야 합니다.")
        return value

    def create(self, validated_data):
        user = validated_data.pop("user")
        product = validated_data.pop("product")

        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("이미 해당 향수에 리뷰를 작성하셨습니다.")

        return Review.objects.create(user=user, product=product, **validated_data)
