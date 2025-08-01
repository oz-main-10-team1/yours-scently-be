from datetime import date

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture
def user():
    return User.objects.create_user(
        email="testuser@example.com",
        password="strongpassword123",
        name="홍길동",
        nickname="길동이",
        gender="MALE",
        birth_date=date(1990, 1, 1),
        phone_number="01012345678",
        is_active=True,
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_user_profile_authenticated(api_client, user):
    # 로그인 (JWT나 Session 방식에 따라 다름. 여기선 force_authenticate 사용)
    api_client.force_authenticate(user=user)

    url = reverse("my-profile")  # name="user-profile"인 URL
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["email"] == user.email
    assert response.data["name"] == user.name
    assert response.data["nickname"] == user.nickname
    assert response.data["gender"] == user.gender
    assert response.data["phone_number"] == user.phone_number
    assert response.data["is_active"] is True


@pytest.mark.django_db
def test_user_profile_unauthenticated(api_client):
    url = reverse("my-profile")
    response = api_client.get(url)

    assert response.status_code == 401
    assert "detail" in response.data
