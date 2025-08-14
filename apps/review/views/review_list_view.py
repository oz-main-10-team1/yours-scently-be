from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import Product
from apps.review.models import Review
from apps.review.pagination import CustomPagination
from apps.review.serializers.review_list_serializer import ReviewListSerializer


class ReviewListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_pagination(self):
        return self.pagination_class()

    @extend_schema(
        summary="향수 리뷰 목록 조회",
        description="특정 향수에 등록된 사용자 리뷰 목록을 조회",
        parameters=[
            OpenApiParameter(
                name="product_id",
                description="조회할 향수 상품의 ID",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="page",
                description="페이지 번호 (기본값: 1)",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="limit",
                description="페이지당 항목 수 (기본값: 10)",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "성공 응답 예시",
                value={
                    "total_count": 2,
                    "page": 1,
                    "limit": 5,
                    "reviews": [
                        {
                            "review_id": 101,
                            "user_nickname": "향기",
                            "rating": 4,
                            "content": "은은하고 부드러운 향이라 데일리로 좋아요.",
                            "created_at": "2025-07-20T14:00:00Z",
                        },
                        {
                            "review_id": 102,
                            "user_nickname": "향",
                            "rating": 3,
                            "content": "생각보다 오래가지 않아요. 그래도 향은 괜찮은 편.",
                            "created_at": "2025-07-19T10:30:00Z",
                        },
                    ],
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "상품을 찾을 수 없음",
                value={"detail": "해당 향수 상품을 찾을 수 없습니다."},
                response_only=True,
                status_codes=["404"],
            ),
        ],
        tags=["review"],
    )
    def get(self, request, product_id: int):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound("해당 향수 상품을 찾을 수 없습니다.")

        # 리뷰 조회
        reviews = Review.objects.filter(product=product).select_related("user").order_by("-created_at")

        # 페이지네이션 적용
        paginator = self.get_pagination()
        paginated_reviews = paginator.paginate_queryset(reviews, request)
        serializer = ReviewListSerializer(paginated_reviews, many=True)

        return paginator.get_paginated_response(serializer.data)
