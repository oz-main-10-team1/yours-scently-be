from django.core.cache import cache
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import Product
from apps.recommendation.serializers.purpose_recommendation_serializer import (
    ProductBannerByCategorySerializer,
)


class ProductBannerByCategoryView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={status.HTTP_200_OK: ProductBannerByCategorySerializer(many=True)},
        description="선택된 카테고리의 향수 반환",
        tags=["recommendation-purpose"],
        parameters=[
            OpenApiParameter(
                name="category",
                description="카테고리 (Daily, Special, Relax, Outdoor 중 하나)",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            )
        ],
    )
    def get(self, request, category: str):
        category = category.capitalize()
        valid_categories = set(Product.Category.values)
        if category not in valid_categories:
            return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"banner_products_{category}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        selected = (
            Product.objects.filter(category=category)
            .select_related("perfume")
            .order_by("?")
            .only("id", "name", "perfume__brand", "price", "product_img_url")[:5]
        )
        serializer = ProductBannerByCategorySerializer(selected, many=True)
        response_data = serializer.data

        cache.set(cache_key, response_data, timeout=60 * 60)

        return Response(response_data)
