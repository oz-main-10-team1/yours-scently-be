from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.review.models import Review
from apps.review.serializers.user_review import UserReviewListSerializer


@extend_schema(
    summary="유저 리뷰 목록 조회",
    tags=["Review"],
    responses={
        200: UserReviewListSerializer,
        400: OpenApiResponse(description="요청 파라미터가 유효하지 않음"),
    },
    examples=[
        OpenApiExample(
            "성공",
            value={
                "reviews": [
                    {
                        "id": 10,
                        "product_id": 3,
                        "product_name": "아쿠아 디 지오",
                        "content": "잔향이 좋았어요",
                        "rating": 4,
                        "created_at": "2025-08-01T15:00:00Z",
                    }
                ],
                "page": 1,
                "size": 10,
                "total": 1,
            },
        ),
        OpenApiExample("실패 - page와 size가 정수가 아님", value={"detail": "page와 size는 정수여야 합니다."}),
    ],
)
class UserReviewsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            page = int(request.query_params.get("page", 1))
            size = int(request.query_params.get("size", 10))
        except ValueError:
            return Response({"detail": "page와 size는 정수여야 합니다."}, status=400)

        page = max(1, page)
        size = max(1, size)

        qs = Review.objects.filter(user=request.user).select_related("product").order_by("-created_at")  # N+1 방지

        total = qs.count()

        start = (page - 1) * size
        end = start + size
        items = list(qs[start:end])

        serializer = UserReviewListSerializer({"reviews": items, "page": page, "size": size, "total": total})
        return Response(serializer.data)
