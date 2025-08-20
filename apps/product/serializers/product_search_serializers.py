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
        perfume = getattr(obj, "perfume", None)
        return getattr(perfume, "brand", "") if perfume else ""

    def get_notes(self, obj) -> List[str]:
        p = getattr(obj, "perfume", None)
        if not p:
            return []

        # 우선순위/합집합으로 수집
        rel_names = ("notes", "main_accords", "top_notes", "middle_notes", "base_notes")
        result: List[str] = []
        seen = set()

        for rel_name in rel_names:
            rel = getattr(p, rel_name, None)
            if not rel:
                continue

            names: List[str] = []
            try:
                # M2M/RelatedManager인 경우 name 필드로 뽑기
                names = list(rel.values_list("name", flat=True))
            except Exception:
                try:
                    # .all() 가능한 경우
                    names = [str(n) for n in rel.all()]
                except Exception:
                    # 문자열/리스트 등 스칼라 처리
                    if isinstance(rel, (list, tuple, set)):
                        names = [str(x) for x in rel]
                    else:
                        names = [str(rel)]

            for n in names:
                if n and n not in seen:
                    seen.add(n)
                    result.append(n)

        return result

    def get_thumbnail_url(self, obj) -> str:
        return str(getattr(obj, "product_img_url", "") or "")

    def get_price(self, obj) -> int:
        val = getattr(obj, "price", 0)
        try:
            return int(val)
        except Exception:
            return 0
