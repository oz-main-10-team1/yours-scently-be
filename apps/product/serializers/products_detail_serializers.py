# apps/product/serializers.py
from rest_framework import serializers

from apps.product.models import Perfume, Product


class PerfumeSerializer(serializers.ModelSerializer):
    perfume_id = serializers.IntegerField(source="id", read_only=True)
    main_accords = serializers.SerializerMethodField()

    class Meta:
        model = Perfume
        fields = [
            "perfume_id",
            "release_year",
            "top_notes",
            "middle_notes",
            "base_notes",
            "main_accords",
            "intensity",
        ]

    def get_main_accords(self, obj):
        return list(obj.main_accords.values_list("name", flat=True))


class ProductDetailSerializer(serializers.ModelSerializer):
    perfume_detail = PerfumeSerializer(source="perfume", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "product_img_url",
            "created_at",
            "perfume_detail",
            "views_count",
        ]
