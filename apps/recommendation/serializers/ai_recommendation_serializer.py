from typing import Any, Dict, Optional

from rest_framework import serializers

from apps.product.models import Product
from apps.recommendation.models import Recommendation, RecommendationHistory


class RecommendationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ["type", "context", "reason", "description"]


class RecommendationHistorySerializer(serializers.ModelSerializer):
    perfume = serializers.SerializerMethodField()

    class Meta:
        model = RecommendationHistory
        fields = ["perfume"]

    def get_perfume(self, obj: RecommendationHistory) -> Dict[str, Any]:
        in_stock = obj.perfume.products.filter(stock__gt=0).order_by("price").first()
        fallback = obj.perfume.products.order_by("price").first()
        picked: Optional[Product] = in_stock or fallback

        return {
            "id": obj.perfume.id,
            "name": obj.perfume.name,
            "brand": obj.perfume.brand,
            "price": float(picked.price) if picked else None,
            "image_url": picked.product_img_url if picked else None,
        }


class RecommendationListSerializer(serializers.ModelSerializer):
    histories = RecommendationHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            "id",
            "type",
            "description",
            "reason",
            "context",
            "created_at",
            "histories",
        ]
