import random
from typing import Any, Dict, List, Optional

import requests
from django.db import transaction
from django.db.models import Case, Prefetch, When
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
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
        operation_id="createRecommendation",
        tags=["recommendations"],
        summary="AI 추천 생성",
        description=(
            "사용자 입력 텍스트(`text`)를 기반으로 Clova AI를 호출하여 키워드·설명·사유를 생성하고, "
            "추천(Recommendation) 및 추천 이력(RecommendationHistory)을 저장합니다. "
            "재고가 있는 상품이 있으면 최저가를 우선 사용하고, 없으면 전체 최저가로 폴백합니다."
        ),
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
            ),
            # 400: 잘못된 요청(예: text 누락, ValidationError 등)
            400: OpenApiResponse(
                response=inline_serializer(
                    name="BadRequest",
                    fields={
                        "detail": serializers.CharField(required=False),
                        "non_field_errors": serializers.ListField(child=serializers.CharField(), required=False),
                        "text": serializers.ListField(child=serializers.CharField(), required=False),
                    },
                ),
                description="잘못된 요청(요청 바디 누락/유효성 실패).",
            ),
            # 401: 인증 실패
            401: OpenApiResponse(
                response=inline_serializer(name="Unauthorized", fields={"detail": serializers.CharField()}),
                description="인증 필요(Authorization 헤더 누락/만료).",
            ),
            # 502: 상위(Clova) 호출 실패(네트워크/HTTP 오류, 비정상 응답)
            502: OpenApiResponse(
                response=inline_serializer(
                    name="UpstreamError",
                    fields={
                        "detail": serializers.CharField(),
                        "upstream": serializers.CharField(help_text="실패한 외부 시스템 식별자", required=False),
                        "request_id": serializers.CharField(required=False),
                    },
                ),
                description="외부 AI(Clova) 호출 실패 또는 비정상 응답.",
            ),
            # 500: 서버 내부 오류(예상치 못한 예외)
            500: OpenApiResponse(
                response=inline_serializer(name="ServerError", fields={"detail": serializers.CharField()}),
                description="서버 내부 오류.",
            ),
        },
        examples=[
            OpenApiExample("요청 예시", value={"text": "따뜻하고 포근한 바닐라 향 추천해줘"}, request_only=True),
            OpenApiExample(
                "성공 201",
                value={
                    "recommendation_id": 1,
                    "description": "따뜻한 '포근한' 분위기를 바탕으로 바닐라와 머스크가 어우러진 향을 추천드려요.",
                    "reason": "감성 키워드 기반, 계절감 고려",
                    "recommendations": [
                        {
                            "perfume": {
                                "id": 101,
                                "name": "Vanilla Dream",
                                "brand": "ScentLab",
                                "price": 59000.0,
                                "image_url": "https://cdn.example.com/images/vanilla.jpg",
                            },
                            "context": "vanilla, musk",
                            "created_at": "2025-08-12T12:34:56+09:00",
                        }
                    ],
                },
                response_only=True,
            ),
            OpenApiExample(
                "실패 400 (text 누락)",
                value={"detail": "text 필드는 필수입니다."},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "실패 401 (미인증)",
                value={"detail": "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."},
                response_only=True,
                status_codes=["401"],
            ),
            OpenApiExample(
                "실패 502 (Clova 호출 실패)",
                value={
                    "detail": "외부 AI 호출 실패",
                    "upstream": "clova",
                    "request_id": "5e9d2c9a-3a86-4c90-9f5d-2f3bf6e2f3f1",
                },
                response_only=True,
                status_codes=["502"],
            ),
            OpenApiExample(
                "실패 500 (서버 내부 오류)",
                value={"detail": "Internal Server Error"},
                response_only=True,
                status_codes=["500"],
            ),
        ],
    )
    @transaction.atomic
    def post(self, request):
        user_input: str = request.data.get("text")
        if not user_input:
            return Response({"detail": "text 필드는 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # Clova 호출 → keywords, description, reason 수신 (ID 제외)
        try:
            clova_response = call_clova_model(user_input)
        except requests.HTTPError as e:
            return Response(
                {
                    "detail": "외부 AI 호출 실패",
                    "upstream": "clova",
                    "request_id": e.request.headers.get("X-NCP-CLOVASTUDIO-REQUEST-ID"),
                },
                status=502,
            )
        except ValueError as e:  # JSON 파싱 실패 등
            return Response({"detail": str(e)}, status=502)
        except Exception:
            return Response({"detail": "Internal Server Error"}, status=500)
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
        operation_id="listRecommendationHistories",
        tags=["recommendations"],
        summary="추천 이력 조회",
        description="로그인 사용자가 생성한 모든 추천(Recommendation)과 각 추천의 히스토리를 최신순으로 반환합니다.",
        responses={
            # 200: {"results": RecommendationList[]}
            200: inline_serializer(
                name="RecommendationHistoryListResponse", fields={"results": RecommendationListSerializer(many=True)}
            ),
            # 401: 인증 실패
            401: OpenApiResponse(
                response=inline_serializer(name="Unauthorized", fields={"detail": serializers.CharField()}),
                description="인증 필요(Authorization 헤더 누락/만료).",
            ),
            # 500: 서버 내부 오류 (옵션)
            500: OpenApiResponse(
                response=inline_serializer(name="ServerError", fields={"detail": serializers.CharField()}),
                description="서버 내부 오류.",
            ),
        },
        examples=[
            OpenApiExample(
                name="성공 200 (데이터 있음)",
                value={
                    "results": [
                        {
                            "id": 12,
                            "type": "ai",
                            "description": "따뜻한 '포근한' 분위기를 바탕으로 바닐라와 머스크가 어우러진 향을 추천드려요.",
                            "reason": "감성 키워드 기반, 계절감 고려",
                            "context": "vanilla, amber",
                            "created_at": "2025-08-12T12:34:56+09:00",
                            "histories": [
                                {
                                    "perfume": {
                                        "id": 101,
                                        "name": "Vanilla Dream",
                                        "brand": "ScentLab",
                                        "price": 59000.0,
                                        "image_url": "https://cdn.example.com/images/vanilla.jpg",
                                    }
                                }
                            ],
                        }
                    ]
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="성공 200 (빈 결과)",
                value={"results": []},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                name="실패 401 (미인증)",
                value={"detail": "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."},
                response_only=True,
                status_codes=["401"],
            ),
        ],
    )
    def get(self, request):
        qs = (
            Recommendation.objects.filter(user=request.user)
            .prefetch_related("histories__perfume__products")
            .order_by("-created_at")
        )
        serializer = RecommendationListSerializer(qs, many=True)
        return Response({"results": serializer.data})
