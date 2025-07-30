from datetime import timedelta

from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
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
        request=UserDeleteSerializer,
        description="회원 탈퇴 API - 회원탈퇴",
        tags=["user"],
        summary="회원 탈퇴",
        responses={200: UserDeleteResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = request.user
            reason = serializer.validated_data["reason"]
            detail = serializer.validated_data.get("detail", "")
            due_date = timezone.now().date() + timedelta(days=14)

            # 이미 탈퇴 요청한 경우 방지
            if hasattr(user, "withdrawal"):
                return Response({"detail": "이미 탈퇴 요청된 사용자입니다."}, status=400)

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

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
