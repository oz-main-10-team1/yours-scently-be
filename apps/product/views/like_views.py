from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import Product, Like
from apps.product.serializers.like_serializer import ProductLikeResponseSerializer


class ProductLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="상품 좋아요 추가",
        responses={200: ProductLikeResponseSerializer, 404: OpenApiResponse(description="존재하지 않는 상품")},
        tags=["Product"],
    )
    # 좋아요
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "존재하지 않는 상품입니다."}, status=404)

        like, _ = Like.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={"is_liked": True},
        )

        return Response({"liked": True}, status=200)

    @extend_schema(
        summary="상품 좋아요 취소",
        responses={200: ProductLikeResponseSerializer, 400: OpenApiResponse(description="찜한 내역이 없습니다."), 404: OpenApiResponse(description="존재하지 않는 상품")},
        tags=["Product"],
    )
    # 좋아요 삭제
    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "존재하지 않는 상품입니다."}, status=404)

        try:
            like = Like.objects.get(user=request.user, product=product)
            if like.is_liked:
                like.is_liked = False
                like.save()
                return Response({"liked": False}, status=200)
            else:
                return Response({"detail": "이미 찜하지 않은 상태입니다."}, status=400)
        except Like.DoesNotExist:
            return Response({"detail": "찜한 내역이 없습니다."}, status=400)