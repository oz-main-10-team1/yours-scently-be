from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import Product
from apps.product.serializers.products_detail_serializers import ProductDetailSerializer


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get("product_id") or kwargs.get("pk")
        if not product_id:
            return Response(
                {"status_code": status.HTTP_400_BAD_REQUEST, "message": "상품 ID가 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(Product, id=product_id)

        # 조회수 증가
        product.views_count = (product.views_count or 0) + 1
        product.save(update_fields=["views_count"])

        serializer = ProductDetailSerializer(product)

        return Response(
            {
                "status_code": status.HTTP_200_OK,
                "message": "데이터를 성공적으로 불러왔습니다.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
