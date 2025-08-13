from __future__ import annotations

from typing import Any, Dict, List

from django.db.models import Q
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.product.models import Perfume
from apps.recommendation.mapping import (
    INTENSITY_MAP,
    KEYWORD_MAP,
    MOOD_MAP,
    USAGE_MAP,
)
from apps.recommendation.serializers.survey_recommendation_reason_serializer import (
    RecommendationReasonRequestSerializer,
    RecommendationReasonResponseSerializer,
)


class RecommendationReasonView(APIView):
    @extend_schema(
        tags=["Recommendation"],
        operation_id="get_recommendation_reason",
        summary="설문조사 향수 추천 사유 제공",
        description=(
            "설문 응답과 특정 향수 ID를 바탕으로 왜 이 향수가 추천되었는지 " "개인화된 추천 사유를 제공합니다"
        ),
        request=RecommendationReasonRequestSerializer,
        responses={
            200: RecommendationReasonResponseSerializer,
            400: OpenApiResponse(description="검증 오류 (필수 값 누락/형식 오류)"),
            404: OpenApiResponse(description="향수를 찾을 수 없음"),
        },
        examples=[
            OpenApiExample(
                name="요청 예시",
                request_only=True,
                value={
                    "perfume_id": 87,
                    "mood": "로맨틱하고 부드러운 느낌",
                    "intensity": "적당한 향이 좋아요",
                    "usage": "특별한 날",
                    "keyword": "사랑스러운",
                },
            ),
            OpenApiExample(
                name="성공 응답 예시",
                response_only=True,
                value={
                    "perfume_id": 87,
                    "reason": "당신이 선호한 향기 노트 'musk', 'rose'가 포함되어 있고, 중간 강도의 향이며 '로맨틱한' 분위기를 지닌 향수입니다.",
                },
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        req_ser = RecommendationReasonRequestSerializer(data=request.data)
        if not req_ser.is_valid():
            return Response(req_ser.errors, status=status.HTTP_400_BAD_REQUEST)

        perfume_id = req_ser.validated_data["perfume_id"]
        mood = req_ser.validated_data["mood"]
        intensity = req_ser.validated_data["intensity"]
        usage = req_ser.validated_data["usage"]
        keyword = req_ser.validated_data["keyword"]

        # 향수확인
        try:
            perfume = (
                Perfume.objects.select_related()
                .prefetch_related("top_notes", "middle_notes", "base_notes", "main_accords", "products")
                .get(id=perfume_id)
            )
        except Perfume.DoesNotExist:
            return Response(
                {"message": "해당 향수를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 추천 사유 생성
        reason = self._generate_reason(perfume, mood, intensity, usage, keyword)

        response_data = {"perfume_id": perfume_id, "reason": reason}

        resp_ser = RecommendationReasonResponseSerializer(response_data)
        return Response(resp_ser.data, status=status.HTTP_200_OK)

    def _generate_reason(self, perfume: Perfume, mood: str, intensity: str, usage: str, keyword: str) -> str:
        reason_parts = []

        # 매칭된 향기 노트 찾기
        matched_notes = self._find_matched_notes(perfume, keyword)
        if matched_notes:
            notes_str = "', '".join(matched_notes)
            reason_parts.append(f"당신이 선호한 향기 노트 '{notes_str}'가 포함되어 있고")

        # 강도 매칭 확인
        intensity_reason = self._get_intensity_reason(perfume, intensity)
        if intensity_reason:
            reason_parts.append(intensity_reason)

        # 분위기 매칭 확인
        mood_reason = self._get_mood_reason(perfume, mood)
        if mood_reason:
            reason_parts.append(mood_reason)

        # 사용 상황 매칭 확인
        usage_reason = self._get_usage_reason(perfume, usage)
        if usage_reason:
            reason_parts.append(usage_reason)

        # 브랜드/제품명 정보 추가
        product_info = self._get_product_info(perfume)
        if product_info:
            reason_parts.append(product_info)

        # 최종 문장 조합
        if reason_parts:
            base_reason = ", ".join(reason_parts)
            return f"{base_reason} 향수입니다."
        else:
            return f"'{perfume.brand} {perfume.name}'은(는) 당신의 취향과 잘 어울리는 향수입니다."

    def _find_matched_notes(self, perfume: Perfume, keyword: str) -> List[str]:
        keyword_targets = KEYWORD_MAP.get(keyword, [])
        if not keyword_targets:
            return []

        matched_notes = []

        # Top, Middle, Base 노트에서 매칭되는 것들 찾기
        all_notes = (
            list(perfume.top_notes.values_list("name", flat=True))
            + list(perfume.middle_notes.values_list("name", flat=True))
            + list(perfume.base_notes.values_list("name", flat=True))
        )

        for note in all_notes:
            if note.lower() in [target.lower() for target in keyword_targets]:
                matched_notes.append(note)

        # 중복 제거
        return list(set(matched_notes))[:3]

    # 강도 사유ㄴ
    def _get_intensity_reason(self, perfume: Perfume, intensity: str) -> str:
        intensity_map = {
            "은은한 향을 좋아해요": "은은하고 부드러운 강도의 향이며",
            "적당한 향이 좋아요": "적당한 강도의 향이며",
            "존재감 있는 강한 향이 좋아요": "존재감 있는 강한 향이며",
        }

        user_intensities = INTENSITY_MAP.get(intensity, [])
        if perfume.intensity in user_intensities:
            return intensity_map.get(intensity, "")
        return ""

    # 분위기 사유
    def _get_mood_reason(self, perfume: Perfume, mood: str) -> str:
        mood_descriptions = {
            "상쾌한 느낌": "상쾌하고 깔끔한",
            "따뜻하고 포근한 느낌": "따뜻하고 포근한",
            "로맨틱하고 부드러운 느낌": "로맨틱하고 부드러운",
            "에너지 넘치고 활기찬 느낌": "에너지 넘치고 활기찬",
            "신비롭고 매혹적인 느낌": "신비롭고 매혹적인",
        }

        mood_targets = MOOD_MAP.get(mood, [])
        perfume_accords = list(perfume.main_accords.values_list("name", flat=True))

        # 매칭되는 어코드가 있는지 확인
        if any(accord in mood_targets for accord in perfume_accords):
            mood_desc = mood_descriptions.get(mood, mood.replace(" 느낌", ""))
            return f"'{mood_desc}' 분위기를 지닌"
        return ""

    # 사용 상황 관련 사유(카테고리)
    def _get_usage_reason(self, perfume: Perfume, usage: str) -> str:
        usage_descriptions = {
            "데일리용": "일상적으로 사용하기 좋은",
            "잠들기 전": "편안한 휴식에 적합한",
            "운동 후": "활동적인 상황에 어울리는",
            "특별한 날": "특별한 순간을 위한",
        }

        usage_code = USAGE_MAP.get(usage)
        if usage_code and perfume.products.filter(category=usage_code).exists():
            return usage_descriptions.get(usage, "")
        return ""

        # 브랜드나 특별한 정보가 있을 때 추가

    def _get_product_info(self, perfume: Perfume) -> str:
        if perfume.brand and len(perfume.brand) > 1:
            return f"'{perfume.brand}'의 시그니처"
        return ""
