from django.db.models import F
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from apps.product.models import Product
from apps.product.serializers.product_serializers import ProductSerializer


class ProductListView(APIView, LimitOffsetPagination):
    """
    상품 목록 조회 (무한 스크롤 + 조회수 증가)
    """

    permission_classes = [IsAuthenticated]
    default_limit = 10
    max_limit = 80

    @extend_schema(
        summary="상품 목록 조회",
        tags=["Product"],
        description="""
        등록된 상품 목록을 무한 스크롤 방식으로 조회합니다.  
        조회 시마다 해당 상품의 조회수가 1 증가합니다.  
        limit, offset 파라미터로 페이지네이션을 적용할 수 있습니다.
        """,
        responses={
            200: ProductSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                "성공",
                value={
                    "status_code": 200,
                    "data": [
                        {
                            "id": 1,
                            "name": "Vanilla Dream",
                            "brand": "ScentLab",
                            "price": "59000.00",
                            "product_img_url": "https://cdn.example.com/images/vanilla.jpg",
                        }
                    ],
                    "message": "상품 목록 조회 성공 (조회수 증가)",
                },
                response_only=True,
            )
        ],
    )
    def get(self, request):
        products = Product.objects.all().order_by("-created_at")

        if not products.exists():
            return Response(
                {"status_code": HTTP_404_NOT_FOUND, "message": "상품목록의 정보를 가지고오지 못했습니다.", "data": []},
                status=HTTP_404_NOT_FOUND,
            )

        paginated_products = self.paginate_queryset(products, request, view=self)

        Product.objects.filter(id__in=[p.id for p in paginated_products]).update(views_count=F("views_count") + 1)

        updated_products = Product.objects.filter(id__in=[p.id for p in paginated_products])
        serializer = ProductSerializer(updated_products, many=True)

        return self.get_paginated_response(
            {"status_code": HTTP_200_OK, "data": serializer.data, "message": "상품 목록 조회 성공 (조회수 증가)"}
        )
