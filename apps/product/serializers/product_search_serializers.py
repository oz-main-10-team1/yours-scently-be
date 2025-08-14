from typing import List

from rest_framework import serializers

from apps.product.models.product import Product


# 쿼리 파라미터 검증
class ProductSearchQuerySerializer(serializers.Serializer):
    keyword = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    note = serializers.ListField(child=serializers.CharField(), required=False)
    price_min = serializers.IntegerField(required=False, min_value=0)
    price_max = serializers.IntegerField(required=False, min_value=0)
    sort = serializers.ChoiceField(required=False, choices=("popularity", "newest", "price_asc", "price_desc"))
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=100, default=10)

    def validate(self, attrs):
        pmin, pmax = attrs.get("price_min"), attrs.get("price_max")
        if pmin is not None and pmax is not None and pmin > pmax:
            raise serializers.ValidationError("가격 범위가 올바르지 않습니다.")
        return attrs


# 응답 아이템
class ProductSearchItemSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()  # Decimal → int

    class Meta:
        model = Product
        fields = ["product_id", "name", "price", "brand", "notes", "thumbnail_url"]

    def get_product_id(self, obj) -> str:
        return str(obj.id)

    def get_brand(self, obj) -> str:
        p = getattr(obj, "perfume", None)
        if not p:
            return ""
        b = getattr(p, "brand", None)
        return getattr(b, "name", str(b)) if b is not None else ""

    def get_notes(self, obj) -> List[str]:
        p = getattr(obj, "perfume", None)
        if not p:
            return []
        # perfume에 notes 또는 main_accords 같은 M2M이 있을 때만 수집
        for rel_name in ("notes", "main_accords"):
            rel = getattr(p, rel_name, None)
            if rel is not None:
                try:
                    return list(rel.values_list("name", flat=True))
                except Exception:
                    return [str(n) for n in rel.all()]
        return []

    def get_thumbnail_url(self, obj) -> str:
        return str(getattr(obj, "product_img_url", "") or "")

    def get_price(self, obj) -> int:
        val = getattr(obj, "price", 0)
        try:
            return int(val)
        except Exception:
            return 0
