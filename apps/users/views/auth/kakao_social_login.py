from typing import Dict

from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import SocialUser, User
from apps.users.serializers.auth.social_login import SocialLoginSerializer
from apps.users.utils.jwt import generate_jwt_tokens_for_user
from apps.users.utils.kakao import (
    format_full_birthday,
    generate_unique_nickname,
    get_kakao_access_token,
    get_kakao_user_info,
    normalize_phone_number,
)


class KakaoLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SocialLoginSerializer,
        responses={200: Dict[str, str], 400: Dict[str, str]},
        tags=["auth"],
        summary="카카오 소셜 로그인",
    )
    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]

        # access_token 요청
        access_token, error = get_kakao_access_token(code)

        if not access_token:
            if "invalid_grant" in (error or ""):
                return Response({"detail": "잘못된 인가 코드입니다."}, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"detail": f"카카오 서버 오류: {error or '알 수 없는 오류'}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 사용자 정보 요청
        user_info = get_kakao_user_info(access_token)
        if not user_info or not user_info.get("email") or not user_info.get("kakao_id"):
            return Response(
                {"detail": "카카오 사용자 정보 요청 실패 또는 필수 정보 누락"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 사용자 정보 파싱
        kakao_id = user_info.get("kakao_id")
        email = user_info.get("email")
        raw_nickname = user_info.get("nickname") or (f"kakao_{email.split('@')[0]}" if email else None)
        nickname = generate_unique_nickname(raw_nickname)
        name = user_info.get("name")
        raw_phone_number = user_info.get("phone_number")
        phone_number = normalize_phone_number(raw_phone_number)
        birthday = format_full_birthday(user_info.get("birthyear"), user_info.get("birthday"))
        gender = user_info.get("gender")

        # 필수값 누락 여부 검사
        required_fields = {
            "kakao_id": kakao_id,
            "email": email,
            "nickname": nickname,
            "name": name,
            "phone_number": phone_number,
            "birthday": birthday,
            "gender": gender,
        }

        # 누락 필드 추출
        missing_fields = [field for field, value in required_fields.items() if not value]

        if missing_fields:
            return Response(
                {"detail": "잠시 후 다시 시도해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 기존 소셜 유저 확인 또는 신규 생성
        with transaction.atomic():
            try:
                social_user = SocialUser.objects.select_related("user").get(provider="KAKAO", provider_id=kakao_id)
                user = social_user.user
            except SocialUser.DoesNotExist:
                user, _ = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "name": name,
                        "nickname": nickname,
                        "phone_number": phone_number,
                        "birth_date": birthday,
                        "gender": gender,
                        "is_active": True,
                    },
                )
                SocialUser.objects.create(user=user, provider="KAKAO", provider_id=kakao_id)

        # JWT 발급
        tokens = generate_jwt_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)
