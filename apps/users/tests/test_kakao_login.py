from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import SocialUser, User
from apps.users.utils.kakao import normalize_phone_number

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def kakao_user_info():
    return {
        "kakao_id": "123456789",
        "email": "test@example.com",
        "nickname": "test",
        "name": "홍길동",
        "phone_number": "010-1234-5678",
        "birthyear": "1995",
        "birthday": "0101",
        "gender": "MALE",
    }


@patch("apps.users.views.auth.kakao_social_login.get_kakao_access_token")
@patch("apps.users.views.auth.kakao_social_login.get_kakao_user_info")
def test_kakao_login_success(mock_user_info, mock_access_token, api_client, kakao_user_info):
    mock_access_token.return_value = ("dummy_access_token", None)
    mock_user_info.return_value = kakao_user_info

    response = api_client.post(reverse("kakao-login"), {"code": "valid_code"}, format="json")

    assert response.status_code == 200
    assert "access_token" in response.data
    assert User.objects.filter(email="test@example.com").exists()
    assert SocialUser.objects.filter(provider="KAKAO", provider_id="123456789").exists()


@patch("apps.users.views.auth.kakao_social_login.get_kakao_access_token")
def test_kakao_login_invalid_code(mock_access_token, api_client):
    mock_access_token.return_value = (None, "invalid_grant")

    response = api_client.post(reverse("kakao-login"), {"code": "bad_code"}, format="json")

    assert response.status_code == 400
    assert response.data["detail"] == "잘못된 인가 코드입니다."


@patch("apps.users.views.auth.kakao_social_login.get_kakao_access_token")
@patch("apps.users.views.auth.kakao_social_login.get_kakao_user_info")
def test_kakao_login_missing_fields(mock_user_info, mock_access_token, api_client):
    mock_access_token.return_value = ("dummy_access_token", None)
    incomplete_user_info = {
        "kakao_id": "123456789",
        "email": None,  # 필수 필드 누락
    }
    mock_user_info.return_value = incomplete_user_info

    response = api_client.post(reverse("kakao-login"), {"code": "valid_code"}, format="json")

    assert response.status_code == 500
    assert "detail" in response.data
