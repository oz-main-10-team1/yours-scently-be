from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.product.models.like import Like
from apps.product.serializers.like_list_serializer import ProductLikeListSerializer


@extend_schema(
    summary="좋아요(찜) 목록 조회",
    tags=["Product"],
    description="로그인 사용자가 찜한 상품 목록을 최신순으로 반환합니다.",
    responses={
        200: ProductLikeListSerializer(many=True),
    },
    examples=[
        OpenApiExample(
            "성공",
            value=[
                {
                    "product_id": 1,
                    "name": "Vanilla Dream",
                    "brand": "ScentLab",
                    "price": "59000.00",
                    "product_img_url": "https://cdn.example.com/images/vanilla.jpg",
                    "is_liked": True,
                    "liked_at": "2025-08-12T12:34:56+09:00",
                }
            ],
            response_only=True,
        )
    ],
)
class ProductLikeListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductLikeListSerializer

    def get_queryset(self):
        return (
            Like.objects.select_related("product").filter(user=self.request.user, is_liked=True).order_by("-updated_at")
        )
