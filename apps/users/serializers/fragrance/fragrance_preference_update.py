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
        # 향 노트 목록 필드 처리: top, middle, base 각각 처리
        for note_type in ["top", "middle", "base"]:
            field_name = f"{note_type}_notes"  # 요청에서 넘어오는 필드명
            model_field_name = f"preferred_{note_type}_notes"  # 실제 모델 필드명

            if field_name in validated_data:
                note_names = validated_data.pop(field_name)
                note_objs = Note.objects.filter(name__in=note_names, type=note_type)
                getattr(instance, model_field_name).set(note_objs)

        # 나머지 필드 (intensity, preferences 등) 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        # 응답 포맷 구성 (모델의 preferred_* 필드를 응답 시 top_notes 등으로 매핑)
        return {
            "user_id": instance.user.id,
            "top_notes": [note.name for note in instance.preferred_top_notes.all()],
            "middle_notes": [note.name for note in instance.preferred_middle_notes.all()],
            "base_notes": [note.name for note in instance.preferred_base_notes.all()],
            "intensity": instance.intensity,
            "preferences": instance.preferences,
            "updated_at": instance.updated_at,
        }
