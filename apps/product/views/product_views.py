from rest_framework import generics, pagination
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.product.models import Product
from apps.product.serializers.product_serializers import ProductSerializer


# ---
# 무한 스크롤을 위한 커스텀 페이지네이션 클래스
# ---
class CustomPagination(pagination.LimitOffsetPagination):
    # 한 페이지에 보여줄 기본 항목 수
    default_limit = 10
    # 클라이언트가 페이지당 항목 수를 지정할 때 사용하는 파라미터 이름
    limit_query_param = "limit"
    # 클라이언트가 요청할 수 있는 최대 항목 수
    max_limit = 100

    def get_paginated_response(self, data):
        """
        페이지네이션된 응답 형식을 정의합니다.
        """
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.count,
                "results": data,
            }
        )


# ---
# 상품 목록을 정렬 및 무한 스크롤로 보여주는 API View
# ---
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        클라이언트의 'order_by' 쿼리 파라미터에 따라 쿼리셋을 필터링하고 정렬합니다.
        """
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
