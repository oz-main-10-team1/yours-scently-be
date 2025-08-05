import uuid

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.product.models import Note
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
    token = res.json().get("access") or res.json().get("access_token")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def preference(user):
    return FragrancePreference.objects.create(user=user, intensity="parfum", preferences={"daytime_use": False})


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
        response = client.patch(url, data={"intensity": "eau_de_toilette"}, format="json")

        assert response.status_code == 401
        assert "인증" in response.json()["detail"]

    def test_update_fragrance_preference_not_found(self, auth_client, user):
        FragrancePreference.objects.filter(user=user).delete()
        url = reverse("fragrance-preference-update")
        response = auth_client.patch(url, data={"intensity": "eau_de_parfum"}, format="json")

        assert response.status_code == 404
        assert "존재하지 않습니다" in response.json()["detail"]
