from rest_framework import serializers

from apps.recommendation.models import Recommendation


class RecommendationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ["type", "context", "reason"]
