from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.users.models import User


class MyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "nickname",
            "birth_date",
            "gender",
            "phone_number",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "email", "created_at", "updated_at", "is_active"]


class MyProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("nickname", "phone_number")
        extra_kwargs = {
            "nickname": {"required": False},
            "phone_number": {"required": False},
        }


# 내정보 수정 - 비밀번호 변경
class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": ["비밀번호가 일치하지 않습니다."]})

        user = self.context["request"].user
        try:
            password_validation.validate_password(data["new_password"], user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        if user.check_password(data["new_password"]):
            raise serializers.ValidationError(
                {"new_password": ["기존 비밀번호와 동일한 비밀번호로 변경할 수 없습니다."]}
            )

        return data


# 닉네임 길이 제한
class NicknameCheckSerializer(serializers.Serializer):
    nickname = serializers.CharField(
        max_length=10,
        required=True,
        error_messages={
            "required": "nickname 필드는 필수입니다.",
            "max_length": "닉네임은 10자 이하로 입력해주세요.",
        },
    )
