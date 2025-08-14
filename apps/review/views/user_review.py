from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.review.models import Review
from apps.review.serializers.user_review import UserReviewListSerializer


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
