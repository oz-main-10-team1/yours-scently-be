from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models.products_exchange_return import (
    ExchangeReturnRequest,
    Product_Exchange,
)
from apps.product.serializers.products_exchange_return_serializers import (
    ProductExchangeSerializer,
)


class ProductExchangeReturnAPIView(APIView):
    # Change the parameter name to match the URL pattern
    def get(self, request, product_exchange_id):
        # ... your code, now using the correct variable name
        try:
            exchange_product = Product_Exchange.objects.get(id=product_exchange_id)
        except Product_Exchange.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update any other queries to use the correct variable name
        exchange_return_requests = ExchangeReturnRequest.objects.filter(
            exchange_return__id=product_exchange_id
        ).order_by("-created_at")

        data = ProductExchangeSerializer(exchange_product).data
        data["exchange_return"] = {
            "requests": [
                {
                    "request_id": str(req.request_id),
                    "type": req.type,
                    "status": req.status,
                    "requests_reason": req.requests_reason,
                }
                for req in exchange_return_requests
            ]
        }
        return Response({"product": data}, status=status.HTTP_200_OK)
