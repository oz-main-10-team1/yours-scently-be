import uuid

import pytest
from decouple import config
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.product.models import Note  # 실제 Note 모델 import

User = get_user_model()

EMAIL = config("EMAIL_HOST_USER")
PASSWORD = "password123"
NICKNAME = f"u{uuid.uuid4().hex[:8]}"[:10]
PHONE_NUMBER = f"010{uuid.uuid4().hex[:8]}"[:11]  # 랜덤한 고유 전화번호


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email=EMAIL, password=PASSWORD, nickname=NICKNAME, phone_number=PHONE_NUMBER, is_active=True
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    res = client.post("/api/token/", {"email": EMAIL, "password": PASSWORD}, format="json")
    assert res.status_code == 200, f"JWT 토큰 발급 실패: {res.content}"
    access_token = res.json()["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return client


@pytest.fixture
def top_notes(db):
    return [
        Note.objects.create(name="Citrus", type="top"),
        Note.objects.create(name="Lavender", type="top"),
    ]


@pytest.fixture
def middle_notes(db):
    return [
        Note.objects.create(name="Rose", type="middle"),
        Note.objects.create(name="Jasmine", type="middle"),
    ]


@pytest.fixture
def base_notes(db):
    return [
        Note.objects.create(name="Sandalwood", type="base"),
        Note.objects.create(name="Vanilla", type="base"),
    ]


@pytest.fixture
def fragrance_payload(top_notes, middle_notes, base_notes):
    return {
        "preferred_top_notes": [note.id for note in top_notes],
        "preferred_middle_notes": [note.id for note in middle_notes],
        "preferred_base_notes": [note.id for note in base_notes],
        "intensity": "eau_de_toilette",
        "preferences": {"daytime_use": False},
    }


@pytest.mark.django_db
def test_register_fragrance_preference_success(auth_client, user, fragrance_payload):
    url = reverse("create-fragrance-preference", kwargs={"user_id": user.id})
    res = auth_client.post(url, data=fragrance_payload, format="json")

    print("응답 내용:", res.content)

    assert res.status_code == 201
    data = res.json()
    assert data["user"] == user.id
    assert data["intensity"] == fragrance_payload["intensity"]


@pytest.mark.django_db
def test_register_fragrance_preference_missing_field(auth_client, user, fragrance_payload):
    url = reverse("create-fragrance-preference", kwargs={"user_id": user.id})
    fragrance_payload.pop("preferred_top_notes")  # 필수 필드 제거

    res = auth_client.post(url, data=fragrance_payload, format="json")
    assert res.status_code in [400, 422]
    assert "preferred_top_notes" in res.json()


@pytest.mark.django_db
def test_register_fragrance_preference_unauthorized(user, fragrance_payload):
    client = APIClient()
    url = reverse("create-fragrance-preference", kwargs={"user_id": user.id})
    res = client.post(url, data=fragrance_payload, format="json")

    assert res.status_code == 401  # 인증 실패


@pytest.mark.django_db
def test_register_fragrance_preference_forbidden(user, fragrance_payload):
    other_user = User.objects.create_user(
        email=f"other_{uuid.uuid4().hex[:5]}@example.com",
        password="password123",
        nickname=f"u{uuid.uuid4().hex[:5]}"[:10],
        phone_number=f"010{uuid.uuid4().hex[:8]}"[:11],
    )

    client = APIClient()
    client.force_authenticate(user=other_user)

    url = reverse("create-fragrance-preference", kwargs={"user_id": user.id})
    res = client.post(url, data=fragrance_payload, format="json")

    assert res.status_code == 403
    assert "권한" in res.json()["detail"]
