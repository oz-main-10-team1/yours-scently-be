from __future__ import annotations

from rest_framework import serializers

from apps.recommendation.mapping import (
    INTENSITY_MAP,
    KEYWORD_MAP,
    MOOD_MAP,
    USAGE_MAP,
)


class RecommendationReasonRequestSerializer(serializers.Serializer):
    perfume_id = serializers.IntegerField(min_value=1, help_text="추천 사유를 알고 싶은 향수의 ID")
    mood = serializers.ChoiceField(
        choices=list(MOOD_MAP.keys()),
        help_text="선호하는 향의 분위기",
        error_messages={"invalid_choice": "올바른 분위기를 선택해주세요.", "required": "분위기는 필수 선택사항입니다."},
    )
    intensity = serializers.ChoiceField(
        choices=list(INTENSITY_MAP.keys()),
        help_text="선호하는 향의 강도",
        error_messages={"invalid_choice": "올바른 강도를 선택해주세요.", "required": "강도는 필수 선택사항입니다."},
    )
    usage = serializers.ChoiceField(
        choices=list(USAGE_MAP.keys()),
        help_text="향수 사용 상황",
        error_messages={
            "invalid_choice": "올바른 사용 상황을 선택해주세요.",
            "required": "사용 상황은 필수 선택사항입니다.",
        },
    )
    keyword = serializers.ChoiceField(
        choices=list(KEYWORD_MAP.keys()),
        help_text="감성 키워드",
        error_messages={"invalid_choice": "올바른 키워드를 선택해주세요.", "required": "키워드는 필수 선택사항입니다."},
    )


class RecommendationReasonResponseSerializer(serializers.Serializer):
    perfume_id = serializers.IntegerField(help_text="향수 ID")
    reason = serializers.CharField(help_text="개인화된 추천 사유")
