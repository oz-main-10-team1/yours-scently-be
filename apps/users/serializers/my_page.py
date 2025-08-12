from rest_framework import serializers

from apps.product.models.perfume import Perfume
from apps.users.models.user import User


class MyPerfumeSerializer(serializers.ModelSerializer):
    main_accords = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Perfume
        fields = ["id", "name", "brand", "main_accords", "intensity"]


# ✅ 조회/수정 응답 공통 포맷
class MyPageSerializer(serializers.ModelSerializer):
    birth_date = serializers.DateField(format="%Y-%m-%d", required=False, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    perfumes = MyPerfumeSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "phone_number",
            "birth_date",
            "gender",
            "created_at",
            "updated_at",
            "perfumes",
        ]


# PATCH 전용(입력 검증)
class MyPageUpdateSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(required=False, min_length=2, max_length=20)
    phone_number = serializers.RegexField(
        regex=r"^010-\d{4}-\d{4}$",
        required=False,
        help_text="하이픈 포함 예: 010-1234-5678",
    )
    birth_date = serializers.DateField(required=False, input_formats=["%Y-%m-%d"])

    class Meta:
        model = User
        fields = ["nickname", "phone_number", "birth_date"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
