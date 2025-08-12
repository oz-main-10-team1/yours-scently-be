# apps/users/tests/test_mypage_update.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models.user import User  


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="testuser@example.com",
        password="testpass123",
        nickname="기존닉네임",
        phone_number="010-1111-2222",
        birth_date="1990-01-01",
        gender="male",
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_update_success(auth_client, user):
    url = reverse("mypage-update")
    payload = {
        "nickname": "새닉네임",
        "phone_number": "010-9876-5432",
        "birth_date": "1995-05-15",
    }
    res = auth_client.patch(url, payload, format="json")

    assert res.status_code == status.HTTP_200_OK
    assert res.data["code"] == 200
    assert res.data["message"] == "마이페이지 정보 수정 성공"
    data = res.data["data"]
    assert data["nickname"] == "새닉네임"
    assert data["phone_number"] == "010-9876-5432"
    assert data["birth_date"] == "1995-05-15"

    user.refresh_from_db()
    assert user.nickname == "새닉네임"
    assert user.phone_number == "010-9876-5432"
    assert str(user.birth_date) == "1995-05-15"


@pytest.mark.django_db
def test_update_invalid_phone_returns_400(auth_client):
    url = reverse("mypage-update")
    res = auth_client.patch(url, {"phone_number": "01012345678"}, format="json")

    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data["code"] == 400
    assert "입력 형식이 잘못되었습니다." in res.data["message"]


@pytest.mark.django_db
def test_update_unauthorized(client):
    url = reverse("mypage-update")
    res = client.patch(url, {"nickname": "익명"}, format="json")

    assert res.status_code == status.HTTP_401_UNAUTHORIZED
