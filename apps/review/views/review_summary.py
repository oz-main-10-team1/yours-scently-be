from django.db.models import Avg
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

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound("해당 향수 상품을 찾을 수 없습니다.")

        reviews = Review.objects.filter(product=product).order_by("-created_at")
        review_count = reviews.count()
        if review_count == 0:
            average_rating = 0.0
        else:
            average_rating = round(reviews.aggregate(ser_rating=Avg("rating"))["ser_rating"] or 0.0, 1)

        latest_reviews = reviews[:3]

        data = {
            "product_id": product.id,
            "average_rating": average_rating,
            "review_count": review_count,
            "latest_reviews": latest_reviews,
        }

        serializer = ReviewSummarySerializer(data)
        return Response(serializer.data)
