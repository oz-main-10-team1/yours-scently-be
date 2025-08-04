import uuid

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import FragrancePreference

User = get_user_model()

# 고정 테스트 유저 정보
EMAIL = f"testuser_{uuid.uuid4().hex[:6]}@example.com"
PASSWORD = "password123"
NICKNAME = f"u{uuid.uuid4().hex[:8]}"[:10]
PHONE_NUMBER = f"010{uuid.uuid4().hex[:8]}"[:11]


@pytest.fixture
def user(db):
    """
    테스트 유저 생성
    """
    return User.objects.create_user(
        email=EMAIL,
        password=PASSWORD,
        nickname=NICKNAME,
        phone_number=PHONE_NUMBER,
        is_active=True,
    )


@pytest.fixture
def auth_client(user):
    """
    이메일 로그인 후 인증된 클라이언트 반환
    """
    client = APIClient()
    login_url = reverse("email-login")  # ✅ email-login 엔드포인트 사용
    res = client.post(login_url, {"email": EMAIL, "password": PASSWORD}, format="json")

    assert res.status_code == 200, f"로그인 실패: {res.content}"

    token_data = res.json()
    access_token = token_data.get("access") or token_data.get("access_token") or token_data.get("token")

    assert access_token, f"access 토큰 없음: {token_data}"
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return client


@pytest.mark.django_db
class TestDeleteFragrancePreference:
    def test_delete_success(self, auth_client, user):
        """
        본인 향기 취향 삭제 성공
        """
        FragrancePreference.objects.create(user=user, intensity="parfum")

        url = f"/api/v1/auth/user/{user.id}/fragrance-preference"  # ✅ prefix 반영
        response = auth_client.delete(url)

        assert response.status_code == 200
        assert response.data["message"] == "사용자 향기 취향이 성공적으로 삭제되었습니다."
        assert not FragrancePreference.objects.filter(user=user).exists()

    def test_delete_unauthorized(self, user):
        """
        인증 없이 삭제 시도 → 401
        """
        FragrancePreference.objects.create(user=user, intensity="parfum")

        client = APIClient()
        url = f"/api/v1/auth/user/{user.id}/fragrance-preference"  # ✅ prefix 반영
        response = client.delete(url)

        assert response.status_code == 401
        assert "인증" in response.data["detail"]

    def test_delete_forbidden(self, user):
        """
        다른 유저의 향기 취향 삭제 시도 → 403
        """
        other = User.objects.create_user(
            email="other@example.com",
            password="password456",
            nickname="tester2",
            phone_number="01011112222",
        )
        FragrancePreference.objects.create(user=other, intensity="eau_de_parfum")

        client = APIClient()
        login_url = reverse("email-login")
        res = client.post(login_url, {"email": EMAIL, "password": PASSWORD}, format="json")
        assert res.status_code == 200

        access_token = res.json().get("access") or res.json().get("access_token") or res.json().get("token")
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = f"/api/v1/auth/user/{other.id}/fragrance-preference"  # ✅ prefix 반영
        response = client.delete(url)

        assert response.status_code == 403
        assert response.data["detail"] == "권한이 없습니다."

    def test_delete_not_found(self, auth_client, user):
        """
        향기 취향이 존재하지 않을 경우 → 404
        """
        FragrancePreference.objects.filter(user=user).delete()

        url = f"/api/v1/auth/user/{user.id}/fragrance-preference"  # ✅ prefix 반영
        response = auth_client.delete(url)

        assert response.status_code == 404
        assert response.data["detail"] == "사용자의 취향 정보가 존재하지 않습니다."
