from django.core.exceptions import FieldDoesNotExist
from django.db.models import (
    ForeignKey,
    ManyToManyField,
    ManyToManyRel,
    OneToOneField,
    Q,
)
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models.product import Product  # ← 프로젝트 경로로 수정
from apps.product.serializers.product_search_serializers import (
    ProductSearchItemSerializer,
    ProductSearchQuerySerializer,
)


def has_field(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
        return True
    except FieldDoesNotExist:
        return False


def is_relation_field(model, name: str) -> bool:
    try:
        f = model._meta.get_field(name)
        return isinstance(f, (ForeignKey, OneToOneField))
    except FieldDoesNotExist:
        return False


def is_m2m_field(model, name: str) -> bool:
    try:
        f = model._meta.get_field(name)
        return isinstance(f, (ManyToManyField, ManyToManyRel))
    except FieldDoesNotExist:
        return False


class ProductSearchAPI(APIView):
    permission_classes = [AllowAny]
# 스웨거 스키마 추가
    @extend_schema(
        summary="상품 검색",
        tags=["Product"],
        parameters=[
            OpenApiParameter(
                name="keyword",
                location=OpenApiParameter.QUERY,
                required=False,
                type=str,
                description="상품/브랜드/향 키워드",
            ),
            OpenApiParameter(
                name="category", location=OpenApiParameter.QUERY, required=False, type=str, description="카테고리"
            ),
            OpenApiParameter(  # ?note=우디&note=프레쉬 형태
                name="note",
                location=OpenApiParameter.QUERY,
                required=False,
                description="향 노트(다중)",
                type={"type": "array", "items": {"type": "string"}},
                style="form",
                explode=True,
            ),
            OpenApiParameter(
                name="price_min", location=OpenApiParameter.QUERY, required=False, type=int, description="최소 가격"
            ),
            OpenApiParameter(
                name="price_max", location=OpenApiParameter.QUERY, required=False, type=int, description="최대 가격"
            ),
            OpenApiParameter(
                name="sort",
                location=OpenApiParameter.QUERY,
                required=False,
                type=str,
                description="popularity | newest | price_asc | price_desc",
            ),
            OpenApiParameter(
                name="page",
                location=OpenApiParameter.QUERY,
                required=False,
                type=int,
                description="페이지 번호(기본 1)",
            ),
            OpenApiParameter(
                name="limit",
                location=OpenApiParameter.QUERY,
                required=False,
                type=int,
                description="페이지 크기(기본 10, 최대 100)",
            ),
        ],
        responses={
            200: inline_serializer(
                name="ProductSearchResponse",
                fields={
                    "total": serializers.IntegerField(),
                    "page": serializers.IntegerField(),
                    "limit": serializers.IntegerField(),
                    "results": ProductSearchItemSerializer(many=True),
                },
            ),
            400: OpenApiResponse(description="검색 조건이 잘못되었습니다."),
        },
    )
    def get(self, request):
        # note는 반복 파라미터 또는 콤마 허용
        raw = request.query_params.copy()
        notes = request.query_params.getlist("note")
        if len(notes) == 1 and "," in notes[0]:
            notes = [n.strip() for n in notes[0].split(",") if n.strip()]
        raw.setlist("note", notes)

        qser = ProductSearchQuerySerializer(data=raw)
        if not qser.is_valid():
            return Response({"detail": "검색 조건이 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

        p = qser.validated_data
        qs = Product.objects.all()

        # keyword: name / description / perfume.name / perfume.brand.name
        kw = p.get("keyword")
        if kw:
            cond = Q(name__icontains=kw)
            if has_field(Product, "description"):
                cond |= Q(description__icontains=kw)

            if has_field(Product, "perfume"):
                cond |= Q(perfume__name__icontains=kw)

                # brand 필드 타입에 따라 안전 분기
                perfume_model = Product._meta.get_field("perfume").remote_field.model
                try:
                    bf = perfume_model._meta.get_field("brand")
                    if isinstance(bf, (ForeignKey, OneToOneField)):
                        # FK/O2O → 조인 후 brand.name 검색
                        cond |= Q(perfume__brand__name__icontains=kw)
                    else:
                        # CharField 등 스칼라 → 직접 검색
                        cond |= Q(perfume__brand__icontains=kw)
                except FieldDoesNotExist:
                    pass

            qs = qs.filter(cond)

        # category(enum 문자열이라고 가정)
        cat = p.get("category")
        if cat and has_field(Product, "category"):
            qs = qs.filter(category__iexact=cat)

        # note: perfume 쪽 M2M(notes/main_accords)에 매칭(AND)
        if has_field(Product, "perfume"):
            perfume_model = Product._meta.get_field("perfume").remote_field.model
            note_fields = ("notes", "main_accords", "top_notes", "middle_notes", "base_notes")

            for n in p.get("note", []) or []:
                cond = Q()
                for field in note_fields:
                    if not has_field(perfume_model, field):
                        continue
                    if is_m2m_field(perfume_model, field) or is_relation_field(perfume_model, field):
                        # 관련 모델에 name이 있는지 확인
                        rel_field = perfume_model._meta.get_field(field)
                        rel_model = rel_field.remote_field.model
                        if has_field(rel_model, "name"):
                            cond |= Q(**{f"perfume__{field}__name__iexact": n})
                        else:
                            # name이 없으면 흔한 대체 필드(label/title/value)도 시도
                            for alt in ("label", "title", "value"):
                                if has_field(rel_model, alt):
                                    cond |= Q(**{f"perfume__{field}__{alt}__iexact": n})
                                    break
                            # 대체 필드가 전혀 없으면 이 필드는 건너뜀
                    else:
                        # 문자 필드인 경우
                        cond |= Q(**{f"perfume__{field}__iexact": n})
                if cond:
                    qs = qs.filter(cond)

        # 가격
        if p.get("price_min") is not None:
            qs = qs.filter(price__gte=p["price_min"])
        if p.get("price_max") is not None:
            qs = qs.filter(price__lte=p["price_max"])

        # 정렬
        sort = p.get("sort")
        if sort == "price_asc":
            qs = qs.order_by("price")
        elif sort == "price_desc":
            qs = qs.order_by("-price")
        elif sort == "newest":
            qs = qs.order_by("-created_at") if has_field(Product, "created_at") else qs.order_by("-id")
        elif sort == "popularity":
            # ERD에 popularity 없음 → 안전한 기본값
            qs = qs.order_by("-id")
        else:
            qs = qs.order_by("-id")

        # 관련 객체 최적화(있을 때만 효과)
        if has_field(Product, "perfume"):
            selects = ["perfume"]
            perfume_model = Product._meta.get_field("perfume").remote_field.model
            if is_relation_field(perfume_model, "brand"):
                selects.append("perfume__brand")
            qs = qs.select_related(*selects)

            prefetches = []
            for f in ("notes", "main_accords", "top_notes", "middle_notes", "base_notes"):
                if has_field(perfume_model, f) and is_m2m_field(perfume_model, f):
                    prefetches.append(f"perfume__{f}")

            if prefetches:
                qs = qs.prefetch_related(*prefetches)
        # 페이지네이션
        page, limit = p.get("page", 1), p.get("limit", 10)
        total = qs.count()
        start, end = (page - 1) * limit, (page - 1) * limit + limit

        data = ProductSearchItemSerializer(qs[start:end], many=True).data
        return Response({"total": total, "page": page, "limit": limit, "results": data}, status=200)
