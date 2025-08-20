import random

from rest_framework import serializers

from apps.product.models import Product


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source="product_img_url", read_only=True)
    brand = serializers.CharField(source="perfume.brand", read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "image_url", "brand", "price", "description", "tags"]

    def get_tags(self, obj):
        tags = []
        tags.extend([main_accord for main_accord in obj.perfume.main_accords.values_list("name", flat=True)])
        tags.extend([main_accord for main_accord in obj.perfume.top_notes.values_list("name", flat=True)])
        tags.extend([main_accord for main_accord in obj.perfume.middle_notes.values_list("name", flat=True)])
        tags.extend([main_accord for main_accord in obj.perfume.base_notes.values_list("name", flat=True)])

        filtered_tags = [item for item in tags if item]
        result = random.sample(filtered_tags, min(len(filtered_tags), 3))
        if obj.volume_ml:
            result = result[:2] + [f"{obj.volume_ml} ml", obj.perfume.get_intensity_display()]
        return result
