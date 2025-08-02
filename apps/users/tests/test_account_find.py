import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import User
from apps.users.models.social_user import SocialUser
from apps.users.utils.redis_utils import (
    mark_reset_email_as_verified,
    store_reset_email_code,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def test_user() -> User:
    return User.objects.create_user(
        email="testuser@example.com", password="securepass123", name="홍길동", phone_number="01012345678"
    )


@pytest.fixture
def verified_phone(monkeypatch):
    monkeypatch.setattr("apps.users.utils.redis_utils.is_email_find_phone_verified", lambda phone: True)


# 이메일 찾기 테스트
def test_email_find_success(api_client: APIClient, test_user: User, verified_phone) -> None:
    url = reverse("email-find")
    response = api_client.post(url, data={"name": test_user.name, "phone_number": test_user.phone_number})
    assert response.status_code == 200
    assert "email" in response.data
    assert response.data["email"].startswith("t")


def test_email_find_not_found(api_client: APIClient, verified_phone) -> None:
    url = reverse("email-find")
    response = api_client.post(url, data={"name": "존재하지않는", "phone_number": "01000000000"})
    assert response.status_code == 404
    assert "message" in response.data


def test_email_find_without_phone_verification(api_client: APIClient, test_user: User, monkeypatch) -> None:
    monkeypatch.setattr("apps.users.views.find_account_views.is_email_find_phone_verified", lambda _: False)
    url = reverse("email-find")
    response = api_client.post(url, data={"name": test_user.name, "phone_number": test_user.phone_number})
    assert response.status_code == 400
    assert response.data["message"] == "휴대폰 인증을 먼저 완료해주세요."


# 비밀번호 재설정 - 이메일 인증코드 발송
def test_password_reset_email_send(api_client: APIClient, test_user: User, monkeypatch) -> None:
    monkeypatch.setattr("apps.users.tasks.send_verification_email_task.delay", lambda email, code: None)
    url = reverse("send-reset-code")
    response = api_client.post(url, data={"email": test_user.email})
    assert response.status_code == 200
    assert "message" in response.data


def test_password_reset_email_send_for_social_user(api_client: APIClient, test_user: User, monkeypatch) -> None:
    SocialUser.objects.create(user=test_user, provider="naver", provider_id="123456")
    url = reverse("send-reset-code")
    response = api_client.post(url, data={"email": test_user.email})
    assert response.status_code == 400
    assert "message" in response.data


def test_password_reset_email_send_user_not_found(api_client: APIClient) -> None:
    url = reverse("send-reset-code")
    response = api_client.post(url, data={"email": "noone@example.com"})
    assert response.status_code == 404
    assert "message" in response.data


# 비밀번호 재설정 - 인증코드 검증
def test_password_reset_verify_code_success(api_client: APIClient, test_user: User) -> None:
    url = reverse("verify-code")
    store_reset_email_code(test_user.email, "ABC123")
    response = api_client.post(url, data={"email": test_user.email, "code": "ABC123"})
    assert response.status_code == 200
    assert "message" in response.data


def test_password_reset_verify_code_fail(api_client: APIClient, test_user: User) -> None:
    url = reverse("verify-code")
    store_reset_email_code(test_user.email, "ABC123")
    response = api_client.post(url, data={"email": test_user.email, "code": "WRONGCODE"})
    assert response.status_code == 400
    assert "message" in response.data


# 비밀번호 변경
def test_password_change_success(api_client: APIClient, test_user: User) -> None:
    url = reverse("change-password")
    mark_reset_email_as_verified(test_user.email)
    data = {
        "email": test_user.email,
        "new_password": "newsecurepass",
        "new_password_confirm": "newsecurepass",
    }
    response = api_client.post(url, data=data)
    assert response.status_code == 200
    assert "message" in response.data


def test_password_change_user_not_found(api_client: APIClient) -> None:
    url = reverse("change-password")
    data = {
        "email": "notfound@example.com",
        "new_password": "newsecurepass",
        "new_password_confirm": "newsecurepass",
    }
    response = api_client.post(url, data=data)
    assert response.status_code == 404
    assert "message" in response.data


def test_password_change_mismatch(api_client: APIClient, test_user: User) -> None:
    url = reverse("change-password")
    data = {
        "email": test_user.email,
        "new_password": "pw1",
        "new_password_confirm": "pw2",
    }
    response = api_client.post(url, data=data)
    assert response.status_code == 400
    assert "non_field_errors" in response.data
