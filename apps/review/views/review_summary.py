from django.db.models import Avg, Count
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import Product
from apps.review.models import Review
from apps.review.serializers.review_summary import ReviewSummarySerializer


class ReviewSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # schema는 전부 작성 후 파일 병합할 때 진행 예정

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

            latest_qs = (reviews_qs.order_by("-created_at").only("id", "user_id", "content", "rating", "created_at"))[
                :3
            ]
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

    def post(self, request, product_id: int):
        return self._build_response(product_id)
