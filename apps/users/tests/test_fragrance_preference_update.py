import uuid

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.product.models import Note
from apps.users.models import FragrancePreference

User = get_user_model()

# 테스트용 고정 정보
EMAIL = f"testuser_{uuid.uuid4().hex[:6]}@example.com"
PASSWORD = "password123"
NICKNAME = f"u{uuid.uuid4().hex[:8]}"[:10]
PHONE_NUMBER = f"010{uuid.uuid4().hex[:8]}"[:11]


# 사용자 생성 fixture
@pytest.fixture
def user(db):
    return User.objects.create_user(
        email=EMAIL,
        password=PASSWORD,
        nickname=NICKNAME,
        phone_number=PHONE_NUMBER,
        is_active=True,
    )


# 로그인 후 인증된 client 반환
@pytest.fixture
def auth_client(user):
    client = APIClient()
    login_url = reverse("email-login")
    res = client.post(login_url, {"email": EMAIL, "password": PASSWORD}, format="json")

    assert res.status_code == 200, f"로그인 실패: {res.content}"

    token_data = res.json()
    access_token = token_data.get("access") or token_data.get("access_token") or token_data.get("token")
    assert access_token, f"access 토큰 없음: {token_data}"

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return client


# 향기 취향 사전 등록 fixture
@pytest.fixture
def preference(user):
    return FragrancePreference.objects.create(user=user, intensity="parfum", preferences={"daytime_use": False})


# PATCH 향기 취향 수정 API 테스트
@pytest.mark.django_db
class TestUpdateFragrancePreference:

    def test_update_fragrance_preference_success(self, auth_client, user, preference):
        url = reverse("fragrance-preference-update")
        payload = {"intensity": "eau_de_parfum", "preferences": {"daytime_use": True}}

        response = auth_client.patch(url, data=payload, format="json")

        assert response.status_code == 200
        assert response.json()["intensity"] == "eau_de_parfum"
        assert response.json()["preferences"]["daytime_use"] is True

    def test_update_fragrance_preference_unauthorized(self, user, preference):
        client = APIClient()
        url = reverse("fragrance-preference-update")
        payload = {"intensity": "eau_de_toilette"}

        response = client.patch(url, data=payload, format="json")

        assert response.status_code == 401
        assert "인증" in response.json()["detail"]

    def test_update_fragrance_preference_not_found(self, auth_client, user):
        # 삭제 후 요청 → 404 처리 확인
        FragrancePreference.objects.filter(user=user).delete()
        url = reverse("fragrance-preference-update")
        payload = {"intensity": "eau_de_parfum"}

        response = auth_client.patch(url, data=payload, format="json")

        assert response.status_code == 404
        assert "존재하지 않습니다" in response.json()["detail"]
