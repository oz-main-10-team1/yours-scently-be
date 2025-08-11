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
        products = list(obj.perfume.products.all())
        in_stock = [p for p in products if p.stock > 0]

        price_val: Optional[float] = None
        image_url: Optional[str] = None

        target = (
            min(in_stock, key=lambda p: p.price)
            if in_stock
            else (min(products, key=lambda p: p.price) if products else None)
        )
        if target:
            price_val = float(target.price)
            image_url = target.product_img_url

        return {
            "id": obj.perfume.id,
            "name": obj.perfume.name,
            "brand": obj.perfume.brand,
            "price": price_val,
            "image_url": image_url,
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
