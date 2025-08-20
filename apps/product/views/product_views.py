from rest_framework import generics, pagination
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.product.models import Product
from apps.product.serializers.product_serializers import ProductSerializer


class CustomPagination(pagination.LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "limit"
    max_limit = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.count,
                "results": data,
            }
        )


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.select_related("perfume").all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        order_by = self.request.query_params.get("order_by", "latest")

        # 정렬 기준과 모델 필드를 매핑하는 딕셔너리
        ordering_fields = {
            "latest": "-created_at",
            "popular": "-views",  # views 필드가 없을 경우 다른 필드로 대체해야 합니다.
            "price_high": "-price",
            "price_low": "price",
        }

        # 'order_by' 파라미터의 유효성 검사
        if order_by not in ordering_fields:
            raise ValidationError(
                detail="유효하지 않은 'order_by' 파라미터입니다. 'latest', 'popular', 'price_high', 'price_low' 중 하나여야 합니다."
            )

        return queryset.order_by(ordering_fields[order_by])
