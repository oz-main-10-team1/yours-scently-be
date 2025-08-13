from rest_framework import serializers

from apps.product.models.products_exchange_return import (
    ExchangeReturnRequest,
    Product_Exchange,
)


class ExchangeReturnRequestSerializer(serializers.ModelSerializer):
    request_id = serializers.UUIDField()
    order_id = serializers.IntegerField(required=False, allow_null=True)  # 모델에 order_id 없으면 제거하세요
    type = serializers.CharField(source="requests_type")
    status = serializers.CharField()
    requested_at = serializers.CharField(source="requests_at")  # DateTimeField면 DateTimeField로 변경하세요
    reason = serializers.CharField(source="requests_reason", allow_blank=True, required=False)

    class Meta:
        model = ExchangeReturnRequest
        fields = [
            "request_id",
            "order_id",
            "type",
            "status",
            "requested_at",
            "reason",
        ]


class ProductExchangeSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source="product_img_url", allow_blank=True, required=False)

    class Meta:
        model = Product_Exchange
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
        exchange_requests = obj.get("exchange_requests")
        if not exchange_requests:
            return {
                "requests": [],
                "is_exchange_available": True,
                "is_return_available": False,
            }
        requests_data = ExchangeReturnRequestSerializer(exchange_requests, many=True).data
        return {
            "requests": requests_data,
            "is_exchange_available": exchange_requests[0].is_exchange_available,
            "is_return_available": exchange_requests[0].is_return_available,
        }
