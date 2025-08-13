from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models.products_exchange_return import (
    ExchangeReturnRequest,
    Product_Exchange,
)


class ProductExchangeReturnAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, products_exchange_id):
        try:
            product_exchange = get_object_or_404(Product_Exchange, id=products_exchange_id)
        except Http404:
            return Response(
                {
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "해당 상품의 ID를 찾을수 없습니다.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "detail": f"서버 에러가 발생했습니다. 잠시후 다시 시도해주세요: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        exchange_requests = ExchangeReturnRequest.objects.filter(exchange_return=product_exchange).order_by(
            "-requests_at"
        )
        requests_data = [
            {
                "request_id": str(req.request_id),
                "order_id": getattr(req, "order_id", None),
                "type": getattr(req, "requests_type", None),  # 필드명 확인 필요
                "status": req.status,
                "requested_at": req.requests_at,
                "reason": req.requests_reason,
                "exchange_return": req.exchange_return,
            }
            for req in exchange_requests
        ]

        response_data = {
            "product": {
                "id": str(product_exchange.id),
                "name": product_exchange.name,
                "description": product_exchange.description,
                "price": float(product_exchange.price),
                "image_url": getattr(product_exchange, "product_image_url", None),  # 필드명 확인 필요
            },
            "exchange_return": {
                "requests": requests_data,
                "is_exchange_available": (
                    exchange_requests.first().is_exchange_available if exchange_requests.exists() else True
                ),
                "is_return_available": (
                    exchange_requests.first().is_return_available if exchange_requests.exists() else False
                ),
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)
