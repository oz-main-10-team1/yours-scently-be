from rest_framework import serializers

from apps.product.models import Note
from apps.users.models import FragrancePreference


class FragrancePreferenceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    # POST 요청 시 사용하는 SlugRelatedField
    preferred_top_notes = serializers.SlugRelatedField(
        many=True, queryset=Note.objects.filter(type="top"), slug_field="name", required=False
    )
    preferred_middle_notes = serializers.SlugRelatedField(
        many=True, queryset=Note.objects.filter(type="middle"), slug_field="name", required=False
    )
    preferred_base_notes = serializers.SlugRelatedField(
        many=True, queryset=Note.objects.filter(type="base"), slug_field="name", required=False
    )

    # PATCH 요청 시 사용하는 노트명 리스트 필드
    top_notes = serializers.ListField(child=serializers.CharField(), required=False)
    middle_notes = serializers.ListField(child=serializers.CharField(), required=False)
    base_notes = serializers.ListField(child=serializers.CharField(), required=False)

    preferences = serializers.JSONField(required=False)

    class Meta:
        model = FragrancePreference
        fields = [
            "user_id",
            "preferred_top_notes",
            "preferred_middle_notes",
            "preferred_base_notes",
            "top_notes",
            "middle_notes",
            "base_notes",
            "intensity",
            "preferences",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user_id", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        # PATCH용 노트 업데이트 처리
        for note_type in ["top", "middle", "base"]:
            patch_field = f"{note_type}_notes"
            model_field = f"preferred_{note_type}_notes"

            if patch_field in validated_data:
                note_names = validated_data.pop(patch_field)
                note_objs = Note.objects.filter(name__in=note_names, type=note_type)
                if len(note_objs) != len(note_names):
                    raise serializers.ValidationError(
                        {patch_field: f"{note_type}_notes 중 일부는 존재하지 않는 노트입니다."}
                    )
                getattr(instance, model_field).set(note_objs)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return {
            "user_id": instance.user.id,
            "top_notes": [n.name for n in instance.preferred_top_notes.all()],
            "middle_notes": [n.name for n in instance.preferred_middle_notes.all()],
            "base_notes": [n.name for n in instance.preferred_base_notes.all()],
            "intensity": instance.intensity,
            "preferences": instance.preferences,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }
