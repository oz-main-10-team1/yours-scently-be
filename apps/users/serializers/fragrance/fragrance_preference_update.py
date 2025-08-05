from rest_framework import serializers

from apps.product.models import Note
from apps.users.models import FragrancePreference


class FragrancePreferenceUpdateSerializer(serializers.ModelSerializer):
    top_notes = serializers.ListField(child=serializers.CharField(), required=False)
    middle_notes = serializers.ListField(child=serializers.CharField(), required=False)
    base_notes = serializers.ListField(child=serializers.CharField(), required=False)
    preferences = serializers.JSONField(required=False)

    class Meta:
        model = FragrancePreference
        fields = [
            "user_id",
            "top_notes",
            "middle_notes",
            "base_notes",
            "intensity",
            "preferences",
            "updated_at",
        ]
        read_only_fields = ["user_id", "updated_at"]

    def update(self, instance, validated_data):
        # 향 노트 필드 직접 처리
        for note_type in ["top", "middle", "base"]:
            field_name = f"{note_type}_notes"
            model_field_name = f"preferred_{note_type}_notes"

            if field_name in validated_data:
                note_names = validated_data.pop(field_name)
                note_objs = Note.objects.filter(name__in=note_names, type=note_type)
                getattr(instance, model_field_name).set(note_objs)

        # 나머지 필드 업데이트는 부모 메서드 호출
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        # N+1 방지를 위해 View에서 prefetch_related 된 객체 기반 처리
        return {
            "user_id": instance.user.id,
            "top_notes": [note.name for note in instance.preferred_top_notes.all()],
            "middle_notes": [note.name for note in instance.preferred_middle_notes.all()],
            "base_notes": [note.name for note in instance.preferred_base_notes.all()],
            "intensity": instance.intensity,
            "preferences": instance.preferences,
            "updated_at": instance.updated_at,
        }
