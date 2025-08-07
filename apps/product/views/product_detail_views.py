from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.product.models import Product


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id') or kwargs.get('pk')
        if not product_id:
            return Response({
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "상품 ID가 제공되지 않았습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "해당 상품의 데이터를 조회할 수 없습니다."
            }, status=status.HTTP_404_NOT_FOUND)

        response_data = {
            "id": product.id,
            "name": product.name,
            "brand": product.brand,
            "description": product.description,
            "price": str(product.price),
            "stock": product.stock,
            "product_img_url": product.product_img_url,
            "created_at": product.created_at.isoformat(),
        }

        if product.perfume:
            perfume = product.perfume
            response_data["perfume_detail"] = {
                "release_year": perfume.release_year,
                "top_notes": perfume.top_notes,
                "middle_notes": perfume.middle_notes,
                "base_notes": perfume.base_notes,
                "main_accords": perfume.main_accords,
                "gender": perfume.gender,
                "intensity": perfume.intensity,
            }

        return Response({
            "status_code": status.HTTP_200_OK,
            "message": "데이터를 성공적으로 불러왔습니다.",
            "data": response_data
        }, status=status.HTTP_200_OK)
