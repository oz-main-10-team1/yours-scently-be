from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

# 직접 정의한 User 모델 import
from apps.users.models import User


class ChangePhoneWithCodeAPITest(APITestCase):
    def setUp(self):
        # 테스트 사용자 생성
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword",
            phone_number="01000000000",
            is_active=True,
        )

        # JWT 액세스 토큰 발급
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # 인증에 사용할 새 번호와 인증번호
        self.new_phone = "01012345678"
        self.verification_code = "123456"

        # 인증번호를 Redis 캐시에 저장
        cache.set(f"verify_code:{self.new_phone}", self.verification_code, timeout=180)

        # Authorization 헤더에 토큰 삽입
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        # API URL
        self.url = reverse("change-phone")

    def test_change_phone_success(self):
        """올바른 인증번호 입력 시 휴대폰 번호가 변경된다"""
        response = self.client.post(self.url, {"phone_number": self.new_phone, "code": self.verification_code})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "휴대폰 번호가 성공적으로 변경되었습니다.")

        # DB에서 사용자 정보 다시 불러와서 확인
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, self.new_phone)

        # 캐시에서 인증번호 제거 확인
        self.assertIsNone(cache.get(f"verify_code:{self.new_phone}"))

    def test_change_phone_invalid_code(self):
        """잘못된 인증번호 입력 시 번호 변경 실패"""
        response = self.client.post(self.url, {"phone_number": self.new_phone, "code": "wrongcode"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"], ["인증번호가 일치하지 않거나 만료되었습니다."])

        # 사용자 번호는 변경되지 않아야 함
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.phone_number, self.new_phone)
