import uuid

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import FragrancePreference

User = get_user_model()

EMAIL = f"testuser_{uuid.uuid4().hex[:6]}@example.com"
PASSWORD = "password123"
NICKNAME = f"u{uuid.uuid4().hex[:8]}"[:10]
PHONE_NUMBER = f"010{uuid.uuid4().hex[:8]}"[:11]


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email=EMAIL,
        password=PASSWORD,
        nickname=NICKNAME,
        phone_number=PHONE_NUMBER,
        is_active=True,
    )


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


@pytest.mark.django_db
class TestDeleteFragrancePreference:
    def test_delete_success(self, auth_client, user):
        FragrancePreference.objects.create(user=user, intensity="parfum")

        url = reverse("fragrance-preference-delete")
        response = auth_client.delete(url)

        assert response.status_code == 200
        assert response.data["message"] == "사용자 향기 취향이 성공적으로 삭제되었습니다."
        assert not FragrancePreference.objects.filter(user=user).exists()

    def test_delete_unauthorized(self, user):
        FragrancePreference.objects.create(user=user, intensity="parfum")

        client = APIClient()
        url = reverse("fragrance-preference-delete")
        response = client.delete(url)

        assert response.status_code == 401
        assert "인증" in response.data["detail"]

    def test_delete_forbidden(self, auth_client):
        other = User.objects.create_user(
            email="other@example.com",
            password="password456",
            nickname="tester2",
            phone_number="01011112222",
        )
        FragrancePreference.objects.create(user=other, intensity="eau_de_parfum")

        response = auth_client.delete(reverse("fragrance-preference-delete"))

        assert response.status_code in [403, 404]

    def test_delete_not_found(self, auth_client, user):
        FragrancePreference.objects.filter(user=user).delete()

        url = reverse("fragrance-preference-delete")
        response = auth_client.delete(url)

        assert response.status_code == 404
        assert response.data["detail"] == "사용자의 취향 정보가 존재하지 않습니다."
