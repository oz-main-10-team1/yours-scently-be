from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import Withdrawal
from apps.users.serializers.withdrawal import (
    UserDeleteResponseSerializer,
    UserDeleteSerializer,
)


class WithdrawalAPIView(APIView):
    serializer_class = UserDeleteSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="회원 탈퇴",
        description="회원이 탈퇴를 요청합니다. 이미 탈퇴 요청한 경우 400 에러를 반환합니다. "
        "탈퇴 요청 시 계정이 비활성화되며, 14일 후 삭제됩니다.",
        tags=["user"],
        request=UserDeleteSerializer,
        responses={
            200: UserDeleteResponseSerializer,
            400: OpenApiResponse(
                description="이미 탈퇴 요청한 사용자",
                response=inline_serializer(name="AlreadyWithdrawn", fields={"detail": serializers.CharField()}),
            ),
        },
        examples=[
            OpenApiExample(
                "성공",
                value={
                    "message": "회원 탈퇴 완료",
                    "email": "user@example.com",
                    "reason": "NOT_SATISFIED",
                    "reason_detail": "서비스 이용 불편",
                    "due_date": "2025-08-26",
                },
                response_only=True,
            ),
            OpenApiExample(
                "실패 - 이미 탈퇴 요청",
                value={"detail": "이미 탈퇴 요청된 사용자입니다."},
                status_codes=["400"],
                response_only=True,
            ),
        ],
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        # 이미 탈퇴 요청한 경우 방지
        if Withdrawal.objects.filter(user=user).exists():
            return Response({"detail": "이미 탈퇴 요청된 사용자입니다."}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        reason = validated_data["reason"]
        detail = validated_data.get("detail", "")
        due_date = timezone.now().date() + timedelta(days=14)

        with transaction.atomic():
            Withdrawal.objects.create(
                user=user,
                reason=reason,
                reason_detail=detail,
                due_date=due_date,
            )

            user.is_active = False
            user.save(update_fields=["is_active"])

        return Response(
            {
                "message": "회원 탈퇴 완료",
                "email": user.email,
                "reason": reason,
                "reason_detail": detail,
                "due_date": due_date,
            },
            status=status.HTTP_200_OK,
        )
