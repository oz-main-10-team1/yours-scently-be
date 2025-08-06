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
def top_notes(db):
    return [Note.objects.create(name="Citrus", type="top"), Note.objects.create(name="Lavender", type="top")]


@pytest.fixture
def middle_notes(db):
    return [Note.objects.create(name="Rose", type="middle"), Note.objects.create(name="Jasmine", type="middle")]


@pytest.fixture
def base_notes(db):
    return [Note.objects.create(name="Sandalwood", type="base"), Note.objects.create(name="Vanilla", type="base")]


@pytest.fixture
def fragrance_payload(top_notes, middle_notes, base_notes):
    return {
        "preferred_top_notes": [n.name for n in top_notes],
        "preferred_middle_notes": [n.name for n in middle_notes],
        "preferred_base_notes": [n.name for n in base_notes],
        "intensity": "eau_de_toilette",
        "preferences": {"daytime_use": False},
    }


@pytest.fixture
def preference(user):
    return FragrancePreference.objects.create(user=user, intensity="parfum", preferences={"daytime_use": False})


@pytest.mark.django_db
class TestFragrancePreference:

    # --- POST ---
    def test_create_success(self, auth_client, fragrance_payload):
        url = reverse("create-fragrance-preference")
        res = auth_client.post(url, data=fragrance_payload, format="json")
        assert res.status_code == 201

    def test_create_duplicate(self, auth_client, fragrance_payload):
        url = reverse("create-fragrance-preference")
        auth_client.post(url, data=fragrance_payload, format="json")
        res = auth_client.post(url, data=fragrance_payload, format="json")
        assert res.status_code == 400
        assert "이미 등록된 향기 취향이 존재합니다." in res.json()["detail"]

    def test_create_unauthorized(self, fragrance_payload):
        url = reverse("create-fragrance-preference")
        client = APIClient()
        res = client.post(url, data=fragrance_payload, format="json")
        assert res.status_code == 401

    # --- PATCH ---
    def test_update_success(self, auth_client, preference):
        url = reverse("fragrance-preference-update")
        res = auth_client.patch(
            url, data={"intensity": "eau_de_parfum", "preferences": {"daytime_use": True}}, format="json"
        )
        assert res.status_code == 200
        assert res.json()["intensity"] == "eau_de_parfum"

    def test_update_not_found(self, auth_client, user):
        FragrancePreference.objects.filter(user=user).delete()
        url = reverse("fragrance-preference-update")
        res = auth_client.patch(url, data={"intensity": "eau_de_parfum"}, format="json")
        assert res.status_code == 404

    def test_update_unauthorized(self, preference):
        url = reverse("fragrance-preference-update")
        client = APIClient()
        res = client.patch(url, data={"intensity": "eau_de_parfum"}, format="json")
        assert res.status_code == 401

    # --- DELETE ---
    def test_delete_success(self, auth_client, preference):
        url = reverse("fragrance-preference-delete")
        res = auth_client.delete(url)
        assert res.status_code == 200
        assert res.json()["message"] == "사용자 향기 취향이 성공적으로 삭제되었습니다."

    def test_delete_not_found(self, auth_client, user):
        FragrancePreference.objects.filter(user=user).delete()
        url = reverse("fragrance-preference-delete")
        res = auth_client.delete(url)
        assert res.status_code == 404

    def test_delete_unauthorized(self, preference):
        url = reverse("fragrance-preference-delete")
        client = APIClient()
        res = client.delete(url)
        assert res.status_code == 401
