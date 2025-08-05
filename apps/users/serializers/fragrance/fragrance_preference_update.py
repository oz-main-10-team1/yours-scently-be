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
        # top_notes, middle_notes, base_notes 처리
        for note_type in ["top", "middle", "base"]:
            field_name = f"{note_type}_notes"
            model_field_name = f"preferred_{note_type}_notes"

            if field_name in validated_data:
                note_names = validated_data.pop(field_name)

                # 노트 객체 필터링
                note_objs = Note.objects.filter(name__in=note_names, type=note_type)

                # 검증 실패: 존재하지 않는 노트가 포함된 경우
                if len(note_objs) != len(note_names):
                    raise serializers.ValidationError(
                        {field_name: f"{note_type}_notes 중 일부는 존재하지 않는 노트입니다."}
                    )

                # M2M 필드에 할당
                getattr(instance, model_field_name).set(note_objs)

        # 나머지 필드 처리 (intensity, preferences 등)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        # 응답 포맷 구성
        return {
            "user_id": instance.user.id,
            "top_notes": [note.name for note in instance.preferred_top_notes.all()],
            "middle_notes": [note.name for note in instance.preferred_middle_notes.all()],
            "base_notes": [note.name for note in instance.preferred_base_notes.all()],
            "intensity": instance.intensity,
            "preferences": instance.preferences,
            "updated_at": instance.updated_at,
        }
