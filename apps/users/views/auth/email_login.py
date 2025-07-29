from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.auth.email_login import EmailLoginSerializer
from core.utils.jwt import generate_jwt_tokens_for_user


# 이메일 로그인 API
class EmailLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=EmailLoginSerializer,
        responses={
            200: OpenApiResponse(description="JWT 토큰 및 유저 정보 반환"),
            400: OpenApiResponse(description="잘못된 요청 또는 인증 실패"),
            500: OpenApiResponse(description="서버 오류"),
        },
        tags=["auth"],
        summary="이메일 로그인",
        description="이메일과 비밀번호를 이용해 로그인하고 JWT 토큰을 발급받습니다.",
    )
    def post(self, request: Request) -> Response:
        try:
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

        except ValidationError as ve:
            # 시리얼라이저의 유효성 검사 실패는 400으로 응답
            return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # 예기치 못한 오류 처리
            return Response(
                {"detail": "서버 내부 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
