from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from apps.product.models import Product
from apps.product.serializers.products_detail_serializers import ProductDetailSerializer


class ProductDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    default_limit = 10
    max_limit = 100

    @extend_schema(
        summary="상품 상세 조회",
        tags=["Product"],
        description="""
        상품 ID를 기반으로 단일 상품의 상세 정보를 조회합니다.  
        DB에 없는 상품의 경우, 특정 더미 데이터 반환 로직이 포함되어 있습니다.
        """,
        responses={
            200: ProductDetailSerializer,
            400: None,
        },
        examples=[
            OpenApiExample(
                "상품 조회 성공 예시",
                value={
                    "status_code": 200,
                    "message": "상품 조회 성공",
                    "data": {
                        "product_id": 15,
                        "name": "시트러스 블라썸",
                        "price": 72000.00,
                        "stock": 35,
                        "product_img_url": "https://cdn.example.com/product15.jpg",
                        "created_at": "2025-07-21T13:25:33Z",
                        "release_year": 2024,
                        "top_notes": ["bergamot", "orange"],
                        "middle_notes": ["jasmine", "peach"],
                        "base_notes": ["cedarwood", "amber"],
                        "main_accords": "fresh citrus floral",
                        "gender": "unisex",
                        "intensity": "moderate",
                    },
                },
                response_only=True,
            ),
            OpenApiExample(
                "잘못된 상품 ID 예시",
                value={
                    "status_code": 400,
                    "message": "잘못된 상품 ID 입니다.",
                    "data": None,
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request, product_id):
        # 1. 더미 데이터 정의
        dummy_product_data = {
            "product_id": 15,
            "name": "시트러스 블라썸",
            "price": 72000.00,
            "stock": 35,
            "product_img_url": "https://cdn.example.com/product15.jpg",
            "created_at": "2025-07-21T13:25:33Z",
            "release_year": 2024,
            "top_notes": ["bergamot", "orange"],
            "middle_notes": ["jasmine", "peach"],
            "base_notes": ["cedarwood", "amber"],
            "main_accords": "fresh citrus floral",
            "gender": "unisex",
            "intensity": "moderate",
        }

        try:
            # 2. DB 조회
            product = Product.objects.get(id=product_id)
            serializer = ProductDetailSerializer(product)
            return Response(
                {
                    "status_code": HTTP_200_OK,
                    "message": "상품 조회 성공",
                    "data": serializer.data,
                },
                status=HTTP_200_OK,
            )
        except Product.DoesNotExist:
            # 3. DB에 없으면 더미 데이터 반환
            if product_id != dummy_product_data["product_id"]:
                return Response(
                    {
                        "status_code": HTTP_400_BAD_REQUEST,
                        "message": "잘못된 상품 ID 입니다.",
                        "data": None,
                    },
                    status=HTTP_400_BAD_REQUEST,
                )

            serializer = ProductDetailSerializer(data=dummy_product_data)
            if not serializer.is_valid():
                return Response(
                    {
                        "status_code": HTTP_400_BAD_REQUEST,
                        "message": "상품 데이터에 필수 정보가 누락되었거나 형식이 잘못되었습니다.",
                        "errors": serializer.errors,
                    },
                    status=HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "status_code": HTTP_200_OK,
                    "message": "상품 조회 성공 (더미 데이터)",
                    "data": serializer.data,
                },
                status=HTTP_200_OK,
            )
