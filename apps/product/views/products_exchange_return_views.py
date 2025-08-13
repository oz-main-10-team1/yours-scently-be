from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.product.models import Product_Exchange, ExchangeReturnRequest
from apps.product.serializers.products_exchange_return_serializers import (
    ProductExchangeSerializer,
    ExchangeReturnRequestSerializer
)


class ProductExchangeReturnAPIView(APIView):
    def get(self, request, product_exchange_id):
        product_exchange = get_object_or_404(Product_Exchange, id=product_exchange_id)

        # ProductExchangeSerializer를 사용하여 product_exchange 객체를 직렬화
        product_data = ProductExchangeSerializer(product_exchange).data

        # exchange_requests 쿼리셋을 필터링하고 정렬합니다.
        exchange_requests = ExchangeReturnRequest.objects.filter(
            exchange_return=product_exchange
        ).order_by("-requested_at")

        # 시리얼라이저를 사용하여 교환/반품 요청 데이터를 직렬화합니다.
        requests_data = ExchangeReturnRequestSerializer(exchange_requests, many=True).data

        # 최종 응답 데이터를 구성합니다.
        response_data = {
            "product": product_data,
            "exchange_return": {
                "requests": requests_data,
                "is_exchange_available": product_exchange.is_exchange_available,
                "is_return_available": product_exchange.is_return_available,
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)
