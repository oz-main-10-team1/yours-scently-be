from __future__ import annotations

from decimal import Decimal

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.recommendation.mapping import KEYWORD_MAP, MOOD_MAP
from apps.recommendation.models import Recommendation, RecommendationHistory
from apps.recommendation.serializers.recommendation_history_serializer import (
    RecommendationHistoryDetailSerializer,
    RecommendationHistoryListSerializer,
)


# 설문 추천 이력 목록 조회
class RecommendationHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Recommendation History"],
        operation_id="list_recommendation_histories",
        summary="설문 추천 이력 목록 조회",
        description="사용자의 설문 추천 이력 목록을 최신순으로 조회합니다.",
        parameters=[
            OpenApiParameter(name="limit", description="조회할 개수 (기본값: 10)", required=False, type=int),
            OpenApiParameter(name="offset", description="시작 위치 (기본값: 0)", required=False, type=int),
        ],
        responses={
            200: RecommendationHistoryListSerializer(many=True),
            401: OpenApiResponse(description="인증 필요"),
        },
        examples=[
            OpenApiExample(
                name="성공 응답 예시",
                response_only=True,
                value=[
                    {
                        "history_id": 83,
                        "recommended_at": "2025-07-21T10:00:00Z",
                        "perfume_count": 2,
                        "first_perfume": {
                            "perfume_id": 11,
                            "perfume_name": "Romantic Musk",
                            "brand": "Fragrance House",
                        },
                    }
                ],
            )
        ],
    )
    def get(self, request):
        # 페이지네이션
        limit = int(request.GET.get("limit", 10))
        offset = int(request.GET.get("offset", 0))

        # 사용자의 추천 이력 조회
        recommendations = (
            Recommendation.objects.filter(user=request.user)
            .prefetch_related("histories__perfume")
            .order_by("-created_at")[offset : offset + limit]
        )

        serializer = RecommendationHistoryListSerializer(recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 설문 추천 이력 상세 조회
class RecommendationHistoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Recommendation History"],
        operation_id="get_recommendation_history_detail",
        summary="설문 추천 이력 상세 조회",
        description="특정 추천 이력의 상세 정보를 조회합니다.",
        responses={
            200: RecommendationHistoryDetailSerializer,
            404: OpenApiResponse(description="추천 이력을 찾을 수 없음"),
            403: OpenApiResponse(description="접근 권한 없음"),
        },
        examples=[
            OpenApiExample(
                name="성공 응답 예시",
                response_only=True,
                value={
                    "history_id": 83,
                    "recommended_at": "2025-07-21T10:00:00Z",
                    "condition": {
                        "preferred_notes": ["rose", "musk"],
                        "disliked_notes": ["citrus"],
                        "preferred_intensity": "moderate",
                        "preferred_mood": ["로맨틱한", "차분한"],
                        "gender": "unisex",
                        "season": "spring",
                    },
                    "recommended_perfumes": [
                        {
                            "perfume_id": 11,
                            "perfume_name": "Romantic Musk",
                            "brand": "Fragrance House",
                            "similarity_score": 0.89,
                        },
                        {
                            "perfume_id": 27,
                            "perfume_name": "Blush Bloom",
                            "brand": "Elegant Scent",
                            "similarity_score": 0.76,
                        },
                    ],
                },
            )
        ],
    )
    # 본인의 이력만 조회 가능
    def get(self, request, history_id):
        recommendation = get_object_or_404(
            Recommendation.objects.filter(user=request.user).prefetch_related(
                "histories__perfume", "histories__perfume__main_accords"
            ),
            id=history_id,
        )

        serializer = RecommendationHistoryDetailSerializer(recommendation)
        return Response(serializer.data, status=status.HTTP_200_OK)


def create_recommendation_history(user, survey_data, recommended_perfumes, recommendation_scores=None):

    conditions = _convert_survey_to_conditions(survey_data)

    recommendation = Recommendation.objects.create(
        user=user,
        survey_conditions=conditions if hasattr(Recommendation, "survey_conditions") else None,
    )

    for idx, perfume in enumerate(recommended_perfumes):
        score = recommendation_scores[idx] if recommendation_scores else None
        decimal_score = Decimal(str(score)) if score is not None else None

        RecommendationHistory.objects.create(
            recommendation=recommendation, perfume=perfume, similarity_score=decimal_score
        )

    return recommendation


def _convert_survey_to_conditions(survey_data):

    mood = survey_data.get("mood")
    keyword = survey_data.get("keyword")
    intensity = survey_data.get("intensity")
    usage = survey_data.get("usage")

    preferred_notes = []
    preferred_mood = []

    if keyword and keyword in KEYWORD_MAP:
        preferred_notes.extend(KEYWORD_MAP[keyword][:3])  # 상위 3개만

    if mood and mood in MOOD_MAP:
        mood_accords = MOOD_MAP[mood][:2]  # 상위 2개만
        preferred_mood.extend(mood_accords)

    intensity_mapping = {
        "은은한 향을 좋아해요": "light",
        "적당한 향이 좋아요": "moderate",
        "존재감 있는 강한 향이 좋아요": "strong",
    }
    preferred_intensity = intensity_mapping.get(intensity, "moderate")

    return {
        "preferred_notes": preferred_notes,
        "preferred_intensity": preferred_intensity,
        "preferred_mood": preferred_mood,
        "usage": usage,
        "original_survey": {"mood": mood, "intensity": intensity, "usage": usage, "keyword": keyword},
    }
