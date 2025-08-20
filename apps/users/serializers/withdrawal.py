from typing import Any

from rest_framework import serializers

from apps.users.models import Withdrawal


class UserDeleteSerializer(serializers.Serializer[Any]):
    reason = serializers.ChoiceField(choices=Withdrawal.Reason.choices)
    detail = serializers.CharField(required=False, allow_blank=True)


class UserDeleteResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    email = serializers.EmailField()
    reason = serializers.CharField()
    reason_detail = serializers.CharField()
    due_date = serializers.DateField()
