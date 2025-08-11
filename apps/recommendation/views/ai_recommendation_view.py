import random
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.db.models import Case, Prefetch, When
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import Perfume, Product
from apps.recommendation.models import Recommendation, RecommendationHistory
from apps.recommendation.serializers.ai_recommendation_serializer import (
    RecommendationCreateSerializer,
    RecommendationListSerializer,
)
from apps.recommendation.utils.ai_recommendation import call_clova_model


def sample_ids(qs, k=5, hard_cap=20_000):
    # ID 개수가 너무 많으면 메모리 방지용 하드캡 (상황 보고 조절)
    ids_qs = qs.values_list("id", flat=True)
    count = ids_qs.count()
    if count == 0:
        return []
    if count <= hard_cap:
        ids = list(ids_qs)
        return random.sample(ids, k=min(k, len(ids)))
    # 크면 리저버 샘플링으로 스트리밍 처리
    sample = []
    for i, _id in enumerate(ids_qs.iterator(chunk_size=2000), start=1):
        if len(sample) < k:
            sample.append(_id)
        else:
            j = random.randint(1, i)
            if j <= k:
                sample[j - 1] = _id
    return sample


class RecommendationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["recommendations"],
        summary="AI 추천 생성",
        description="사용자 입력 텍스트를 기반으로 Clova AI가 추천을 생성하고 저장합니다.",
        request=inline_serializer(
            name="RecommendationCreateRequest",
            fields={"text": serializers.CharField(help_text="추천 생성에 사용할 텍스트")},
        ),
        responses={
            201: inline_serializer(
                name="RecommendationCreateResponse",
                fields={
                    "recommendation_id": serializers.IntegerField(),
                    "description": serializers.CharField(),
                    "reason": serializers.CharField(),
                    "recommendations": serializers.ListField(
                        child=inline_serializer(
                            name="RecommendationCreateResponseItem",
                            fields={
                                "perfume": inline_serializer(
                                    name="PerfumeBrief",
                                    fields={
                                        "id": serializers.IntegerField(),
                                        "name": serializers.CharField(),
                                        "brand": serializers.CharField(),
                                        "price": serializers.FloatField(allow_null=True),
                                        "image_url": serializers.CharField(allow_null=True),
                                    },
                                ),
                                "context": serializers.CharField(),
                                "created_at": serializers.DateTimeField(),
                            },
                        )
                    ),
                },
            )
        },
        examples=[
            OpenApiExample(
                "요청 예시",
                value={"text": "따뜻하고 포근한 바닐라 향 추천해줘"},
                request_only=True,
            ),
        ],
    )
    @transaction.atomic
    def post(self, request):
        user_input: str = request.data.get("text")
        if not user_input:
            return Response({"detail": "text 필드는 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # Clova 호출 → keywords, description, reason 수신 (ID 제외)
        clova_response = call_clova_model(user_input)
        keywords: List[str] = clova_response.get("keywords", []) or []
        description: str = clova_response.get("description", "") or ""
        reason: str = clova_response.get("reason", "") or ""

        # 후보 생성 (키워드 → main_accords 매칭) → 랜덤 ID 샘플 추출
        base_qs = Perfume.objects.filter(main_accords__name__in=keywords).distinct()
        ids = sample_ids(base_qs, k=5)
        if not ids:
            ids = sample_ids(Perfume.objects.all(), k=5)

        # id 순서 보존 + products Prefetch (재고>0 최저가 우선, 없으면 전체 최저가 폴백)
        preserved = Case(*[When(id=_id, then=pos) for pos, _id in enumerate(ids)]) if ids else None
        in_stock_prefetch = Prefetch(
            "products",
            queryset=Product.objects.filter(stock__gt=0).order_by("price"),
            to_attr="in_stock_products",
        )
        all_sorted_prefetch = Prefetch(
            "products",
            queryset=Product.objects.all().order_by("price"),
            to_attr="all_products_sorted",
        )

        perfumes_qs = Perfume.objects.filter(id__in=ids).prefetch_related(in_stock_prefetch, all_sorted_prefetch)
        if preserved is not None:
            perfumes_qs = perfumes_qs.order_by(preserved)
        perfumes: List[Perfume] = list(perfumes_qs)

        # Recommendation 저장
        payload = {
            "type": Recommendation.Type.AI,
            "context": ", ".join(keywords),
            "reason": reason,
            "description": description,
        }
        serializer = RecommendationCreateSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        recommendation: Recommendation = serializer.save(user=request.user)

        # 추천 이력 저장
        RecommendationHistory.objects.bulk_create(
            [RecommendationHistory(recommendation=recommendation, perfume=p) for p in perfumes]
        )

        # 응답 구성
        results: List[Dict[str, Any]] = []
        for p in perfumes:
            picked: Optional[Product] = None
            in_stock: Optional[List[Product]] = getattr(p, "in_stock_products", None)
            all_sorted: Optional[List[Product]] = getattr(p, "all_products_sorted", None)

            if in_stock:
                picked = in_stock[0]
            elif all_sorted:
                picked = all_sorted[0]

            price: Optional[float] = float(picked.price) if picked else None
            image_url: Optional[str] = picked.product_img_url if picked else None

            results.append(
                {
                    "perfume": {
                        "id": p.id,
                        "name": p.name,
                        "brand": p.brand,
                        "price": price,
                        "image_url": image_url,
                    },
                    "context": ", ".join(keywords),
                    "created_at": recommendation.created_at.isoformat(),
                }
            )

        return Response(
            {
                "recommendation_id": recommendation.id,
                "description": recommendation.description,
                "reason": recommendation.reason,
                "recommendations": results,
            },
            status=status.HTTP_201_CREATED,
        )


class RecommendationHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["recommendations"],
        summary="추천 이력 조회",
        description="내가 생성한 모든 추천과 각 추천에 포함된 향수 이력을 최신순으로 반환합니다.",
        responses={200: RecommendationListSerializer(many=True)},
    )
    def get(self, request):
        qs = (
            Recommendation.objects.filter(user=request.user)
            .prefetch_related("histories__perfume__products")
            .order_by("-created_at")
        )
        serializer = RecommendationListSerializer(qs, many=True)
        return Response({"results": serializer.data})
