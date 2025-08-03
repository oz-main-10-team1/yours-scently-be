from rest_framework import serializers

from apps.product.models import Note
from apps.users.models.fragrance_preference import FragrancePreference


class FragrancePreferenceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    preferred_top_notes = serializers.SlugRelatedField(
        many=True, queryset=Note.objects.filter(type="top"), slug_field="name"
    )
    preferred_middle_notes = serializers.SlugRelatedField(
        many=True, queryset=Note.objects.filter(type="middle"), slug_field="name"
    )
    preferred_base_notes = serializers.SlugRelatedField(
        many=True, queryset=Note.objects.filter(type="base"), slug_field="name"
    )

    class Meta:
        model = FragrancePreference
        fields = [
            "user_id",
            "preferred_top_notes",
            "preferred_middle_notes",
            "preferred_base_notes",
            "intensity",
            "preferences",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user_id", "created_at", "updated_at"]
