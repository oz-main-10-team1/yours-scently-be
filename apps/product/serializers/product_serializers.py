from rest_framework import serializers

from apps.product.models import Product


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source="get_image_url", read_only=True)
    # price 필드를 커스텀 메소드로 처리하려면 SerializerMethodField 사용
    price = serializers.SerializerMethodField()
    release_date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = Product
        fields = ["id", "name", "image_url", "brand", "price", "release_date", "description"]

    def get_price(self, obj):
        # obj.price가 숫자가 아니거나 None일 경우를 대비한 예외 처리 필요
        try:
            return int(obj.price)  # 소수점 없이 "정수 원 단위" 반환
        except (ValueError, TypeError):
            return None  # 또는 적절한 기본값
