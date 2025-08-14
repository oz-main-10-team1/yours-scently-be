from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models.products_exchange_return import ProductExchange, ExchangeReturnRequest
from apps.product.serializers.products_exchange_return_serializers import (
    ProductExchangeReturnResponseSerializer,
)


class ProductExchangeReturnAPIView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='product_exchange_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='Product exchange UUID'
            )
        ],
        responses={200: ProductExchangeReturnResponseSerializer}
    )
    def get(self, request, *args, **kwargs):
        product_exchange_id = kwargs.get("product_exchange_id")
        try:
            exchange_product = ProductExchange.objects.get(id=product_exchange_id)
        except ProductExchange.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        exchange_requests = ExchangeReturnRequest.objects.filter(
            exchange_return=exchange_product
        ).order_by("-created_at")

        # Serializer에 바로 넘겨서 처리
        serializer = ProductExchangeReturnResponseSerializer({
            "product": exchange_product,
            "exchange_requests": exchange_requests,
            "is_exchange_available": exchange_product.is_exchange_available,  # 여기 수정
        })
        return Response(serializer.data, status=status.HTTP_200_OK)
