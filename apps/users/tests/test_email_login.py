import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import User

pytestmark = pytest.mark.django_db  # DB 접근 허용


@pytest.fixture
def test_user() -> User:
    # 테스트용 사용자 생성
    return User.objects.create_user(
        email="test@example.com",
        password="testpassword123",
        nickname="테스터",
        name="홍길동",
        phone_number="01012345678",
    )


def test_email_login_success(test_user: User) -> None:
    client = APIClient()
    url = reverse("email-login")  # URL name 등록 필요

    # 올바른 로그인 요청
    response = client.post(
        url,
        {
            "email": "test@example.com",
            "password": "testpassword123",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "access_token" in response.data
    assert "refresh_token" in response.data
    assert response.data["user"]["email"] == "test@example.com"
    assert response.data["user"]["nickname"] == "테스터"


def test_email_login_wrong_password(test_user: User) -> None:
    client = APIClient()
    url = reverse("email-login")

    # 비밀번호 틀림
    response = client.post(
        url,
        {
            "email": "test@example.com",
            "password": "wrongpassword",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "non_field_errors" in response.data or "detail" in response.data


def test_email_login_inactive_user(test_user: User) -> None:
    test_user.is_active = False
    test_user.save()

    client = APIClient()
    url = reverse("email-login")

    # 비활성화된 사용자 로그인
    response = client.post(
        url,
        {
            "email": "test@example.com",
            "password": "testpassword123",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "non_field_errors" in response.data or "detail" in response.data
