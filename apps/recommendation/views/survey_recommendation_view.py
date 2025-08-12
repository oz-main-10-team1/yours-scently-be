from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

import numpy as np
from django.db.models import Q
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
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
from apps.recommendation.serializers.survey_recommendation_serializer import (
    PerfumeBriefSerializer,
    RecommendationRequestSerializer,
)

_EMBED_MODEL: SentenceTransformer | None = None


def get_embed_model() -> SentenceTransformer:
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        _EMBED_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _EMBED_MODEL


class PerfumeRecommendationView(APIView):
    @extend_schema(
        tags=["Recommendation"],
        operation_id="recommend_one_perfume_from_survey",
        summary="설문 기반 향수 1개 추천",
        description=(
            "설문 응답을 바탕으로 매핑 기반 필터링을 수행한 뒤, sentence-transformers 임베딩 코사인 유사도로 "
            "최종 점수가 가장 높은 향수 1개를 반환합니다."
        ),
        request=RecommendationRequestSerializer,
        responses={
            200: PerfumeBriefSerializer,
            400: OpenApiResponse(description="검증 오류 (필수 값 누락/형식 오류)"),
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
            OpenApiExample(
                name="성공 응답 예시",
                response_only=True,
                value={
                    "id": 123,
                    "name": "Light Breeze",
                    "brand": "Acme",
                    "intensity": "eau_de_toilette",
                    "main_accords": ["fresh", "green"],
                    "score": 0.8421,
                },
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        req_ser = RecommendationRequestSerializer(data=request.data)
        if not req_ser.is_valid():
            return Response(req_ser.errors, status=status.HTTP_400_BAD_REQUEST)

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

        best: Tuple[dict, float] | None = None
        for p in candidates:
            perfume_text = self._make_perfume_text(p)
            p_vec = self._safe_encode(model, perfume_text)
            sim = self._cosine(survey_vec, p_vec)

            item = {
                "id": p.id,
                "name": getattr(p, "name", None) or "",
                "brand": getattr(p, "brand", None) or "",
                "intensity": getattr(p, "intensity", None),
                "main_accords": list(p.main_accords.values_list("name", flat=True)),
                "score": float(round(sim, 6)),
            }
            if (best is None) or (sim > best[1]):
                best = (item, sim)

        assert best is not None
        resp_ser = PerfumeBriefSerializer(best[0])
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
