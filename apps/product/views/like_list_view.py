from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.product.models.like import Like
from apps.product.serializers.like_list_serializer import ProductLikeListSerializer


@extend_schema(
    summary="좋아요(찜) 목록 조회",
    tags=["Product"],
    description="로그인한 사용자가 찜한 상품 목록을 조회합니다.",
    responses={200: ProductLikeListSerializer(many=True)},
)
class ProductLikeListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductLikeListSerializer

    def get_queryset(self):
        return (
            Like.objects.select_related("product").filter(user=self.request.user, is_liked=True).order_by("-updated_at")
        )
