from rest_framework import serializers

from apps.product.models.perfume import Perfume
from apps.users.models.user import User


class MyPerfumeSerializer(serializers.ModelSerializer):
    main_accords = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Perfume
        fields = [
            "id",
            "name",
            "brand",
            "main_accords",
            "intensity",
        ]


class MyPageSerializer(serializers.ModelSerializer):
    # ✅ 실제 User 모델에 연결된 필드명 사용 (예: perfumes)
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
            "perfumes",
        ]

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