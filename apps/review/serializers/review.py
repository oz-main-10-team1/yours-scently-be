from rest_framework import serializers

from apps.review.models import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "product_id", "user_id", "content", "rating", "created_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        product = self.context["product"]
        return Review.objects.create(user=user, product=product, **validated_data)
