from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import Product
from apps.product.models.like import Like
from apps.product.serializers.like_serializer import ProductLikeResponseSerializer


# 찜하기
class LikeTrueAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Product"],
        summary="상품 찜 추가",
        description="로그인한 사용자가 상품을 찜합니다.",
        responses={
            200: OpenApiResponse(ProductLikeResponseSerializer),
            401: OpenApiResponse(description="로그인 필요"),
            404: OpenApiResponse(description="존재하지 않는 상품입니다."),
        },
    )
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "존재하지 않는 상품입니다."}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(user=request.user, product=product)

        if not like.is_liked:
            like.is_liked = True
            like.save()

        return Response({"liked": True}, status=status.HTTP_200_OK)


# 찜 취소
class LikeFalseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Product"],
        summary="상품 찜 취소",
        description="로그인한 사용자가 상품에 눌러둔 찜을 취소합니다.",
        responses={
            200: OpenApiResponse(ProductLikeResponseSerializer),
            400: OpenApiResponse(description="찜한 내역이 없습니다."),
            401: OpenApiResponse(description="로그인 필요"),
            404: OpenApiResponse(description="존재하지 않는 상품입니다."),
        },
    )
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "존재하지 않는 상품입니다."}, status=status.HTTP_404_NOT_FOUND)

        try:
            like = Like.objects.get(user=request.user, product=product)
        except Like.DoesNotExist:
            return Response({"detail": "찜한 내역이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        if not like.is_liked:
            return Response({"detail": "이미 찜하지 않은 상태입니다."}, status=status.HTTP_400_BAD_REQUEST)

        like.is_liked = False
        like.save()

        return Response({"liked": False}, status=status.HTTP_200_OK)
