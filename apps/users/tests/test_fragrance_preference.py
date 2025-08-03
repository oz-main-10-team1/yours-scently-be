import uuid

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.product.models import Note

User = get_user_model()

EMAIL = "testuser@example.com"
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

    print("로그인 응답:", res.json())

    assert res.status_code == 200, f"이메일 로그인 실패: {res.content}"

    token_data = res.json()
    access_token = token_data.get("access") or token_data.get("access_token") or token_data.get("token")

    assert access_token, f"access 토큰 없음: {token_data}"  # 없을 경우 에러 메시지 출력
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
        "preferred_top_notes": [note.name for note in top_notes],
        "preferred_middle_notes": [note.name for note in middle_notes],
        "preferred_base_notes": [note.name for note in base_notes],
        "intensity": "eau_de_toilette",
        "preferences": {"daytime_use": False},
    }


@pytest.mark.django_db
def test_register_fragrance_preference_success(auth_client, fragrance_payload):
    url = reverse("create-fragrance-preference")
    res = auth_client.post(url, data=fragrance_payload, format="json")

    assert res.status_code == 201
    data = res.json()
    assert data["intensity"] == fragrance_payload["intensity"]
    assert set(data["preferred_top_notes"]) == set(fragrance_payload["preferred_top_notes"])


@pytest.mark.django_db
def test_register_fragrance_preference_missing_field(auth_client, fragrance_payload):
    url = reverse("create-fragrance-preference")
    fragrance_payload.pop("preferred_top_notes")

    res = auth_client.post(url, data=fragrance_payload, format="json")
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "preferred_top_notes" in res.json()


@pytest.mark.django_db
def test_register_fragrance_preference_unauthorized(fragrance_payload):
    client = APIClient()
    url = reverse("create-fragrance-preference")
    res = client.post(url, data=fragrance_payload, format="json")
    assert res.status_code == 401


@pytest.mark.django_db
def test_register_fragrance_preference_duplicate(auth_client, user, fragrance_payload):
    url = reverse("create-fragrance-preference")

    res1 = auth_client.post(url, data=fragrance_payload, format="json")
    assert res1.status_code == 201

    res2 = auth_client.post(url, data=fragrance_payload, format="json")
    assert res2.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in res2.json()
    assert "이미 등록된 향기 취향이 존재합니다." in res2.json()["detail"]
