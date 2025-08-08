from rest_framework import serializers

from apps.product.models import Product


class ProductBannerByCategorySerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source="perfume.brand", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "price",
            "product_img_url",
        ]
