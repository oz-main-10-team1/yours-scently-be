from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import SocialUser, User

pytestmark = pytest.mark.django_db


NAVER_USER_INFO = {
    "id": "naver123456789",
    "email": "naveruser@example.com",
    "nickname": "네이버닉네임",
    "name": "홍길동",
    "mobile": "010-1234-5678",
    "birthyear": "1995",
    "birthday": "12-25",
    "gender": "M",
}


@pytest.fixture
def client():
    return APIClient()


@patch("apps.users.views.auth.naver_social_login.get_naver_access_token")
@patch("apps.users.views.auth.naver_social_login.verify_naver_token")
def test_naver_login_success(mock_verify_token, mock_get_token, client):
    mock_get_token.return_value = "mocked-access-token"
    mock_verify_token.return_value = NAVER_USER_INFO

    url = reverse("naver-login")
    payload = {"code": "mocked-code", "state": "mocked-state"}

    response = client.post(url, payload, HTTP_REFERER="https://localhost:3000/")

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.data
    assert "refresh_token" in response.data

    user = User.objects.get(email=NAVER_USER_INFO["email"])
    assert user.nickname == NAVER_USER_INFO["nickname"]
    assert SocialUser.objects.filter(user=user, provider=SocialUser.Provider.NAVER).exists()


@patch("apps.users.views.auth.naver_social_login.verify_naver_token")
@patch("apps.users.views.auth.naver_social_login.get_naver_access_token")
def test_naver_login_access_token_failure(mock_get_token, mock_verify_token, client):
    mock_get_token.return_value = None
    mock_verify_token.return_value = None

    url = reverse("naver-login")
    payload = {"code": "invalid-code"}

    response = client.post(url, payload, HTTP_REFERER="https://localhost:3000/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "네이버 토큰 발급에 실패했습니다" in response.data["detail"]


@patch("apps.users.views.auth.naver_social_login.get_naver_access_token")
@patch("apps.users.views.auth.naver_social_login.verify_naver_token")
def test_naver_login_missing_required_fields(mock_verify_token, mock_get_token, client):
    mock_get_token.return_value = "mocked-token"
    incomplete_info = NAVER_USER_INFO.copy()
    del incomplete_info["email"]
    mock_verify_token.return_value = incomplete_info

    url = reverse("naver-login")
    payload = {"code": "mocked-code"}

    response = client.post(url, payload, HTTP_REFERER="https://localhost:3000/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "필수 정보 누락" in response.data["detail"]


@patch("apps.users.views.auth.naver_social_login.get_naver_access_token")
@patch("apps.users.views.auth.naver_social_login.verify_naver_token")
def test_naver_login_existing_email_without_social_account(mock_verify_token, mock_get_token, client):
    mock_get_token.return_value = "mocked-access-token"
    mock_verify_token.return_value = NAVER_USER_INFO

    # 기존 유저 생성 (소셜 연동 없이)
    User.objects.create(
        email=NAVER_USER_INFO["email"], name="기존유저", nickname="기존닉", phone_number="010-9999-9999"
    )

    url = reverse("naver-login")
    payload = {"code": "mocked-code"}

    response = client.post(url, payload, HTTP_REFERER="https://localhost:3000/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "이미 가입된 이메일입니다" in response.data["detail"]
