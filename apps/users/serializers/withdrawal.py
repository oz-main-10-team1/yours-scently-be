from typing import Any

from rest_framework import serializers


class UserDeleteSerializer(serializers.Serializer[Any]):
    reason = serializers.CharField(max_length=255)
    detail = serializers.CharField()


class UserDeleteResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    email = serializers.EmailField()
    reason = serializers.CharField()
    reason_detail = serializers.CharField()
    due_date = serializers.DateField()