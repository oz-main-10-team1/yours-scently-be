from rest_framework import serializers

from apps.product.models.like import Like


class ProductLikeListSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id")
    name = serializers.CharField(source="product.name")
    brand = serializers.CharField(source="product.brand")
    price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2)
    product_img_url = serializers.CharField(source="product.product_img_url")
    liked_at = serializers.DateTimeField(source="updated_at")

    class Meta:
        model = Like
        fields = [
            "product_id",
            "name",
            "brand",
            "price",
            "product_img_url",
            "is_liked",
            "liked_at",
        ]
