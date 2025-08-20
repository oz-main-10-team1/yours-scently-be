from django.contrib.auth import authenticate
from rest_framework import serializers


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data: dict) -> dict:
        user = authenticate(email=data["email"], password=data["password"])
        if user and user.is_active:
            data["user"] = user
            return data
        raise serializers.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다.")
