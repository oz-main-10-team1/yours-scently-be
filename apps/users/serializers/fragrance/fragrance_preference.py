from rest_framework import serializers

from apps.product.models import Accord, Note
from apps.users.models.fragrance_preference import FragrancePreference


class FragrancePreferenceSerializer(serializers.ModelSerializer):
    # user_id는 읽기 전용 필드로 응답에 포함
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    # 필수로 입력받아야 할 필드들
    preferred_top_notes = serializers.PrimaryKeyRelatedField(many=True, required=True, queryset=Note.objects.all())
    preferred_middle_notes = serializers.PrimaryKeyRelatedField(many=True, required=True, queryset=Note.objects.all())
    preferred_base_notes = serializers.PrimaryKeyRelatedField(many=True, required=True, queryset=Note.objects.all())
    preferred_accords = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=Accord.objects.all())

    class Meta:
        model = FragrancePreference
        fields = [
            "user_id",
            "user",
            "preferred_top_notes",
            "preferred_middle_notes",
            "preferred_base_notes",
            "preferred_accords",
            "intensity",
            "preferences",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]
