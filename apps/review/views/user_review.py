from typing import List

from django.core.paginator import EmptyPage, Paginator
from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.review.models import Review
from apps.review.serializers.user_review import UserReviewListSerializer


class UserReviewsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        size = int(request.query_params.get("size", 10))

        qs: QuerySet[Review] = (
            Review.objects.filter(user=request.user)
            .select_related("product", "product__perfume")
            .order_by("-created_at")
        )

        paginator = Paginator(qs, size)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages) if paginator.num_pages else []

        items: List[Review] = list(page_obj.object_list) if hasattr(page_obj, "object_list") else []

        payload = {
            "reviews": items,
            "page": page if paginator.count else 1,
            "size": size,
            "total": paginator.count,
        }

        serializer = UserReviewListSerializer(payload)
        return Response(serializer.data)
