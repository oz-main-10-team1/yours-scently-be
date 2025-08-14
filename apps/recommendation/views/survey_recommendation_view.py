from __future__ import annotations

import json
import logging
from typing import Dict, Iterable, List, Tuple

import numpy as np
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
from pgvector.django import CosineDistance
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from sentence_transformers import SentenceTransformer

from apps.product.models import Perfume
from apps.recommendation.mapping import (
    INTENSITY_MAP,
    KEYWORD_MAP,
    MOOD_MAP,
    USAGE_MAP,
)
from apps.recommendation.models import Recommendation, RecommendationHistory
from apps.recommendation.serializers.survey_recommendation_serializer import (
    PerfumeBriefSerializer,
    RecommendationRequestSerializer,
)

logger = logging.getLogger(__name__)

_EMBED_MODEL: SentenceTransformer | None = None


def get_embed_model() -> SentenceTransformer:
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        _EMBED_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _EMBED_MODEL


class PerfumeRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Recommendation"],
        operation_id="recommend_one_perfume_from_survey",
        summary="설문 기반 향수 1개 추천",
        description=(
            "설문 응답을 바탕으로 매핑 기반 필터링을 수행 "
            "최종 점수가 가장 높은 향수 1개를 반환 로그인한 사용자의 경우 추천 이력이 자동으로 저장"
        ),
        request=RecommendationRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="추천 성공",
                examples=[
                    OpenApiExample(
                        name="성공 응답 예시",
                        value={
                            "id": 123,
                            "name": "Light Breeze",
                            "brand": "Acme",
                            "intensity": "eau_de_toilette",
                            "main_accords": ["fresh", "green"],
                            "score": 0.8421,
                            "history_id": 456,  # 이력 저장 성공시에만 포함
                        },
                    )
                ],
            ),
            400: OpenApiResponse(description="검증 오류 (필수 값 누락/형식 오류)"),
            401: OpenApiResponse(description="인증 필요"),
            404: OpenApiResponse(description="조건에 맞는 후보가 없음"),
        },
        examples=[
            OpenApiExample(
                name="요청 예시",
                request_only=True,
                value={
                    "mood": "상쾌한 느낌",
                    "intensity": "적당한 향이 좋아요",
                    "usage": "데일리용",
                    "keyword": "사랑스러운",
                },
            ),
        ],
    )

    # 설문 기반 향수 추천 (이력 저장 기능 추가)
    def post(self, request, *args, **kwargs):

        # 요청 데이터 검증
        req_ser = RecommendationRequestSerializer(data=request.data)
        if not req_ser.is_valid():
            return Response(req_ser.errors, status=status.HTTP_400_BAD_REQUEST)

        # 설문 데이터 추출
        mood = req_ser.validated_data["mood"]
        intensity = req_ser.validated_data["intensity"]
        usage = req_ser.validated_data["usage"]
        keyword = req_ser.validated_data["keyword"]

        # 1차 매핑 필터
        mood_targets = MOOD_MAP.get(mood, [])
        intensities = INTENSITY_MAP.get(intensity, [])
        usage_code = USAGE_MAP.get(usage)
        keyword_targets = KEYWORD_MAP.get(keyword, [])

        base_q = Q()
        if mood_targets:
            base_q &= Q(main_accords__name__in=mood_targets)
        if intensities:
            base_q &= Q(intensity__in=intensities)
        if usage_code:
            base_q &= Q(products__category=usage_code)
        if keyword_targets:
            base_q &= (
                Q(top_notes__name__in=keyword_targets)
                | Q(middle_notes__name__in=keyword_targets)
                | Q(base_notes__name__in=keyword_targets)
            )

        candidates = (
            Perfume.objects.filter(base_q)
            .distinct()
            .prefetch_related("top_notes", "middle_notes", "base_notes", "main_accords", "products")
        )

        # 후보가 없으면 완전 실패 대신 점진적 완화
        if not candidates.exists():
            relaxed_q = Q()
            if mood_targets:
                relaxed_q |= Q(main_accords__name__in=mood_targets)
            if keyword_targets:
                relaxed_q |= (
                    Q(top_notes__name__in=keyword_targets)
                    | Q(middle_notes__name__in=keyword_targets)
                    | Q(base_notes__name__in=keyword_targets)
                )
            candidates = (
                Perfume.objects.filter(relaxed_q)
                .distinct()
                .prefetch_related("top_notes", "middle_notes", "base_notes", "main_accords", "products")
            )

        if not candidates.exists():
            return Response(
                {"message": "조건에 맞는 향수를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 임베딩 유사도 보정
        survey_text = self._make_survey_text(mood, intensity, usage, keyword)
        model = get_embed_model()
        survey_vec = self._safe_encode(model, survey_text)

        # pgvector를 사용한 DB 수준 코사인 유사도 검색
        candidates_with_embedding = (
            candidates.filter(embedding__isnull=False)
            .annotate(similarity=1 - CosineDistance("embedding", survey_vec))  # 1 - distance = similarity
            .order_by("-similarity")  # 유사도 높은 순으로 정렬
        )

        best_perfume = None
        similarity_score = 0.5  # fallback 점수

        if candidates_with_embedding.exists():
            best_perfume = candidates_with_embedding.first()
            similarity_score = best_perfume.similarity
        else:
            if candidates.exists():
                best_perfume = candidates.first()
                similarity_score = 0.5
            else:
                return Response(
                    {"message": "조건에 맞는 향수를 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        item = {
            "id": best_perfume.id,
            "name": getattr(best_perfume, "name", None) or "",
            "brand": getattr(best_perfume, "brand", None) or "",
            "intensity": getattr(best_perfume, "intensity", None),
            "main_accords": list(best_perfume.main_accords.values_list("name", flat=True)),
            "score": float(round(similarity_score, 6)),
        }

        if request.user.is_authenticated:
            try:
                history = self._create_recommendation_history(
                    user=request.user,
                    survey_data={"mood": mood, "intensity": intensity, "usage": usage, "keyword": keyword},
                    recommended_perfume=best_perfume,
                    recommendation_score=similarity_score,
                )
                item["history_id"] = history.id

            except Exception as e:
                # 이력 저장 실패해도 추천 결과는 반환
                logger.warning(f"추천 이력 저장 실패: {e}")

        resp_ser = PerfumeBriefSerializer(item)
        return Response(resp_ser.data, status=status.HTTP_200_OK)

    def _make_survey_text(self, mood: str, intensity: str, usage: str, keyword: str) -> str:
        return (
            f"mood: {mood}; intensity: {intensity}; usage: {usage}; keyword: {keyword}. "
            f"mood_targets={','.join(MOOD_MAP.get(mood, []))}; "
            f"keyword_targets={','.join(KEYWORD_MAP.get(keyword, []))}"
        )

    def _make_perfume_text(self, p: Perfume) -> str:
        accords = ", ".join(p.main_accords.values_list("name", flat=True))

        def names(qs) -> List[str]:
            try:
                return list(qs.values_list("name", flat=True))
            except Exception:
                return []

        notes = names(p.top_notes.all()) + names(p.middle_notes.all()) + names(p.base_notes.all())
        notes_joined = ", ".join(notes)
        brand = getattr(p, "brand", "")
        name = getattr(p, "name", "")
        intensity = getattr(p, "intensity", "")
        return f"{brand} {name}. accords: {accords}. notes: {notes_joined}. intensity: {intensity}."

    def _safe_encode(self, model: SentenceTransformer, text: str) -> np.ndarray:
        vec = model.encode(text, convert_to_numpy=True, normalize_embeddings=False)
        if not isinstance(vec, np.ndarray):
            vec = np.array(vec)
        return vec

    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        an = np.linalg.norm(a)
        bn = np.linalg.norm(b)
        if an == 0.0 or bn == 0.0:
            return 0.0
        return float(np.dot(a, b) / (an * bn))

    # 추천 이력 생성 헬퍼 함수
    def _create_recommendation_history(self, user, survey_data, recommended_perfume, recommendation_score):
        recommendation = Recommendation.objects.create(
            user=user,
            type=Recommendation.Type.SURVEY,
            description="설문 기반 향수 추천",
            reason="사용자 설문 응답을 바탕으로 한 개인화 추천",
            context=json.dumps(survey_data, ensure_ascii=False),  # 설문 데이터를 JSON으로 저장
        )

        history = RecommendationHistory.objects.create(
            recommendation=recommendation, perfume=recommended_perfume, similarity_score=float(recommendation_score)
        )

        return recommendation
