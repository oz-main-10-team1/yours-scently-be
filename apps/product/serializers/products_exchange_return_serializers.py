from rest_framework import serializers

from apps.product.models.products_exchange_return import (
    ExchangeReturnRequest,
    ProductExchange,
)


class ExchangeReturnRequestSerializer(serializers.ModelSerializer):
    request_id = serializers.UUIDField()
    type = serializers.CharField()
    status = serializers.CharField()
    reason = serializers.CharField(source="requests_reason", allow_blank=True, required=False)

    class Meta:
        model = ExchangeReturnRequest
        fields = [
            "request_id",
            # "order_id", # 모델에 없는 필드이므로 제거
            "type",
            "status",
            "reason",
        ]


class ProductExchangeSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source="product_img_url", allow_blank=True, required=False)

    class Meta:
        model =  ProductExchange
        fields = [
            "id",
            "name",
            "description",
            "price",
            "image_url",
        ]


class ProductExchangeReturnResponseSerializer(serializers.Serializer):
    product = ProductExchangeSerializer()
    exchange_return = serializers.SerializerMethodField()

    def get_exchange_return(self, obj):
        exchange_requests = obj.get("exchange_requests", [])
        product = obj.get("product")  # ProductExchange 객체 가져오기

        if not exchange_requests:
            return {
                "requests": [],
                "is_exchange_available": getattr(product, "is_exchange_available", True),
                "is_return_available": getattr(product, "is_return_available", False),
            }

        requests_data = ExchangeReturnRequestSerializer(exchange_requests, many=True).data

        return {
            "requests": requests_data,
            "is_exchange_available": getattr(product, "is_exchange_available", True),
            "is_return_available": getattr(product, "is_return_available", False),
        }