from rest_framework import serializers

from apps.product.models import Product


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source="product_img_url", read_only=True)
    brand = serializers.CharField(source="perfume.brand", read_only=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "image_url", "brand", "price", "description"]

    def get_price(self, obj):
        if obj.price is None:
            return None
        try:
            return int(obj.price)
        except (ValueError, TypeError):
            return None
