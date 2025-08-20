from __future__ import annotations

from rest_framework import serializers

from apps.product.models import Perfume
from apps.recommendation.mapping import (
    INTENSITY_MAP,
    KEYWORD_MAP,
    MOOD_MAP,
    USAGE_MAP,
)


class RecommendationRequestSerializer(serializers.Serializer):
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


class PerfumeBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    name = serializers.CharField(max_length=100, allow_blank=False)
    brand = serializers.CharField(max_length=50, allow_blank=False)
    intensity = serializers.ChoiceField(choices=Perfume.IntensityChoices.choices, allow_null=True, required=False)
    main_accords = serializers.ListField(child=serializers.CharField(max_length=50), allow_empty=True)
    score = serializers.FloatField(min_value=0.0, max_value=1.0, help_text="임베딩 코사인 유사도 점수 (0.0 ~ 1.0)")
    history_id = serializers.IntegerField(required=False)
