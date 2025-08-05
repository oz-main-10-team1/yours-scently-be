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


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")

        if len(data["new_password"]) < 8:
            raise serializers.ValidationError("비밀번호는 8자 이상이어야 합니다.")

        user = self.context["request"].user
        if user.check_password(data["new_password"]):
            raise serializers.ValidationError("기존 비밀번호와 동일한 비밀번호로 변경할 수 없습니다.")

        return data
