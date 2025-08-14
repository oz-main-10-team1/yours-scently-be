from django.db.models import Avg, Count
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import Product
from apps.review.models import Review
from apps.review.serializers.review_summary import ReviewSummarySerializer


@extend_schema(
    summary="상품 리뷰 요약 조회",
    tags=["Review"],
    responses={
        200: ReviewSummarySerializer,
        404: OpenApiResponse(description="존재하지 않는 향수 상품"),
    },
    examples=[
        OpenApiExample(
            "성공",
            value={
                "product_id": 1,
                "average_rating": 4.2,
                "review_count": 5,
                "latest_reviews": [
                    {
                        "id": 10,
                        "user_id": 3,
                        "content": "산뜻한 향이에요.",
                        "rating": 4,
                        "created_at": "2025-08-01T12:00:00Z",
                    },
                    {
                        "id": 9,
                        "user_id": 4,
                        "content": "생각보다 향이 강했어요.",
                        "rating": 3,
                        "created_at": "2025-07-28T09:00:00Z",
                    },
                ],
            },
        ),
        OpenApiExample(
            "실패 - 존재하지 않는 상품",
            value={"detail": "해당 향수 상품을 찾을 수 없습니다."},
        ),
    ],
)
class ReviewSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _build_response(self, product_id: int) -> Response:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound("해당 향수 상품을 찾을 수 없습니다.")

        reviews_qs = Review.objects.filter(product=product)
        summary = reviews_qs.aggregate(
            review_count=Count("id"),
            average_rating=Avg("rating"),
        )

        review_count = int(summary.get("review_count") or 0)

        if review_count == 0:
            average_rating = 0.0
            latest_reviews = []
        else:
            average_rating = round(float(summary.get("average_rating") or 0.0), 1)

            latest_qs = (
                reviews_qs.select_related("user")
                .order_by("-created_at")
                .only("id", "user_id", "content", "rating", "created_at")[:3]
            )
            latest_reviews = list(latest_qs)

        payload = {
            "product_id": product.id,
            "average_rating": average_rating,
            "review_count": review_count,
            "latest_reviews": latest_reviews,
        }
        serializer = ReviewSummarySerializer(payload)
        return Response(serializer.data)

    def get(self, request, product_id: int):
        return self._build_response(product_id)
