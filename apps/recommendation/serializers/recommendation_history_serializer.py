import json

from rest_framework import serializers

from apps.product.models import Perfume
from apps.recommendation.models import Recommendation, RecommendationHistory


# 추천된 향수 정보
class RecommendedPerfumeSerializer(serializers.Serializer):
    perfume_id = serializers.IntegerField(source="perfume.id")
    perfume_name = serializers.CharField(source="perfume.name")
    brand = serializers.CharField(source="perfume.brand")
    similarity_score = serializers.DecimalField(max_digits=5, decimal_places=4, allow_null=True)


# 목록용 추천된 향수 간단 정보
class RecommendedPerfumeBriefSerializer(serializers.Serializer):
    perfume_id = serializers.IntegerField(source="perfume.id")
    perfume_name = serializers.CharField(source="perfume.name")
    brand = serializers.CharField(source="perfume.brand")


# 추천 이력 목록 시리얼라이저
class RecommendationHistoryListSerializer(serializers.ModelSerializer):
    history_id = serializers.IntegerField(source="id")
    recommended_at = serializers.DateTimeField(source="created_at")
    recommendation_type = serializers.CharField(source="type")
    perfume_count = serializers.IntegerField()
    first_perfume = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = ["history_id", "recommended_at", "recommendation_type", "perfume_count", "first_perfume"]

    def get_first_perfume(self, obj):
        first_history = obj.histories.all()[0] if obj.histories.all() else None
        if first_history:
            return RecommendedPerfumeBriefSerializer(first_history).data
        return None


# 추천 이력 상세 시리얼라이저
class RecommendationHistoryDetailSerializer(serializers.ModelSerializer):
    history_id = serializers.IntegerField(source="id")
    recommended_at = serializers.DateTimeField(source="created_at")
    recommendation_type = serializers.CharField(source="type")
    condition = serializers.SerializerMethodField()
    recommended_perfumes = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = ["history_id", "recommended_at", "recommendation_type", "condition", "recommended_perfumes"]

    # context 필드에 JSON 형태로 저장된 설문 데이터 파싱
    def get_condition(self, obj):
        try:

            if obj.context:
                return json.loads(obj.context)
        except (json.JSONDecodeError, TypeError):
            pass

        return {"mood": "", "intensity": "", "usage": "", "keyword": ""}

    def get_recommended_perfumes(self, obj):
        histories = obj.histories.select_related("perfume").order_by("created_at")
        return RecommendedPerfumeSerializer(histories, many=True).data


# 추천 이력 생성용 시리얼라이저
class RecommendationHistoryCreateSerializer(serializers.Serializer):
    survey_data = serializers.JSONField(help_text="설문 응답 데이터")
    perfume_ids = serializers.ListField(child=serializers.IntegerField(), help_text="추천된 향수 ID 리스트")
    scores = serializers.ListField(
        child=serializers.DecimalField(max_digits=5, decimal_places=4),
        required=False,
        help_text="추천 점수 리스트 (선택사항)",
    )
    recommendation_type = serializers.ChoiceField(
        choices=Recommendation.Type.choices, default=Recommendation.Type.SURVEY, help_text="추천 유형"
    )

    def validate(self, data):
        perfume_ids = data["perfume_ids"]
        scores = data.get("scores", [])

        if scores and len(scores) != len(perfume_ids):
            raise serializers.ValidationError("점수 리스트 길이가 향수 ID 리스트와 일치하지 않습니다.")

        existing_perfume_ids = set(Perfume.objects.filter(id__in=perfume_ids).values_list("id", flat=True))
        invalid_ids = set(perfume_ids) - existing_perfume_ids
        if invalid_ids:
            raise serializers.ValidationError(f"존재하지 않는 향수 ID: {list(invalid_ids)}")

        return data


# 단일 추천 이력 항목 시리얼라이저 (RecommendationHistory 모델용)
class RecommendationHistoryItemSerializer(serializers.ModelSerializer):
    perfume_id = serializers.IntegerField(source="perfume.id")
    perfume_name = serializers.CharField(source="perfume.name")
    brand = serializers.CharField(source="perfume.brand")
    recommendation_id = serializers.IntegerField(source="recommendation.id")

    class Meta:
        model = RecommendationHistory
        fields = ["id", "perfume_id", "perfume_name", "brand", "similarity_score", "recommendation_id", "created_at"]
