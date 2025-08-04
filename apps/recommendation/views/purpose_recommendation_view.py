import random

from django.core.cache import cache
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
            .order_by("?")
            .only("id", "name", "brand", "price", "product_img_url")[:5]
        )
        serializer = ProductBannerByCategorySerializer(selected, many=True)
        response_data = serializer.data

        cache.set(cache_key, response_data, timeout=60 * 60)

        return Response(response_data)
