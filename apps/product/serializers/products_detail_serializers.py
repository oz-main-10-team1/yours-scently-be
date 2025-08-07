# apps/product/serializers.py

from rest_framework import serializers
from apps.product.models import Product, Perfume


class PerfumeSerializer(serializers.ModelSerializer):
    perfume_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Perfume
        fields = [
            "perfume_id",
            "release_year",
            "top_notes",
            "middle_notes",
            "base_notes",
            "main_accords",
            "gender",
            "intensity",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    perfume_detail = PerfumeSerializer(source='perfume', read_only=True)
    price = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "description",
            "price",
            "stock",
            "product_img_url",
            "created_at",
            "perfume_detail",
        ]

    def get_price(self, obj):
        return str(obj.price)
