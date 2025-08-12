from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.auth.email_login import EmailLoginSerializer
from apps.users.utils.jwt import generate_jwt_tokens_for_user


# 이메일 로그인 API
class EmailLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="이메일 로그인",
        tags=["auth"],
        description="이메일과 비밀번호로 로그인하고 JWT 토큰을 발급합니다.",
        request=EmailLoginSerializer,
        responses={
            200: inline_serializer(
                name="EmailLoginSuccess",
                fields={
                    "access_token": serializers.CharField(),
                    "refresh_token": serializers.CharField(),
                    "user": inline_serializer(
                        name="LoginUser",
                        fields={
                            "id": serializers.IntegerField(),
                            "email": serializers.EmailField(),
                            "nickname": serializers.CharField(allow_null=True, required=False),
                        },
                    ),
                },
            ),
            400: OpenApiResponse(
                description="잘못된 요청 또는 인증 실패",
                response=inline_serializer(name="EmailLoginBadRequest", fields={"detail": serializers.CharField()}),
            ),
            500: OpenApiResponse(
                description="서버 오류",
                response=inline_serializer(name="EmailLoginServerError", fields={"detail": serializers.CharField()}),
            ),
        },
        examples=[
            OpenApiExample(
                "성공 200",
                value={
                    "access_token": "eyJhbGciOi...",
                    "refresh_token": "eyJhbGciOi...",
                    "user": {"id": 1, "email": "user@example.com", "nickname": "상일"},
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "실패 400 (인증 실패)",
                value={"detail": "이메일 또는 비밀번호가 올바르지 않습니다."},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request: Request) -> Response:
        serializer = EmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user: User = serializer.validated_data["user"]
        tokens = generate_jwt_tokens_for_user(user)

        return Response(
            {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "user": {
                    "id": user.id,  # type: ignore[attr-defined]
                    "email": user.email,
                    "nickname": user.nickname,
                },
            },
            status=status.HTTP_200_OK,
        )
