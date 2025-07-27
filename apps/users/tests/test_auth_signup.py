from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.utils.redis_utils import is_phone_verified, is_signup_email_verified

client = APIClient()


@pytest.mark.django_db
@patch("apps.users.tasks.send_verification_email_task.delay")
def test_email_send_and_verify(mock_send_email_task):
    email = "test@example.com"
    code = "123456"

    # 이메일 인증 요청
    response = client.post(reverse("email-send-code"), {"email": email})
    assert response.status_code == 200
    mock_send_email_task.assert_called_once()

    # Redis에 수동으로 인증 코드 저장
    from apps.users.utils.redis_utils import (
        mark_signup_email_as_verified,
        store_signup_email_code,
    )

    store_signup_email_code(email, code)

    # 이메일 인증 코드 검증
    response = client.post(reverse("email-verify"), {"email": email, "verification_code": code})
    assert response.status_code == 200
    assert is_signup_email_verified(email)


@pytest.mark.django_db
@patch("apps.users.views.auth.phone_auth.send_sms_verification_code")
@patch("apps.users.serializers.auth.phone_auth.check_verification_code")
def test_phone_send_and_verify(mock_check_code, mock_send_sms, client):
    phone = "01058249190"
    normalized = "+821058249190"

    mock_send_sms.return_value = None
    mock_check_code.return_value = "approved"

    response = client.post(reverse("phone-send-code"), {"phone": phone})
    assert response.status_code == 200
    mock_send_sms.assert_called_once()

    response = client.post(reverse("phone-verify"), {"phone": phone, "code": "123456"})
    assert response.status_code == 200
    assert is_phone_verified(normalized)


@pytest.mark.django_db
def test_signup_after_email_and_phone_verification():
    email = "signup@example.com"
    phone = "01058249190"
    normalized_phone = "+821058249190"

    from apps.users.utils.redis_utils import (
        is_phone_verified,
        is_signup_email_verified,
        mark_phone_verified,
        mark_signup_email_as_verified,
    )

    mark_signup_email_as_verified(email)
    mark_phone_verified(normalized_phone)

    assert is_signup_email_verified(email) is True
    assert is_phone_verified(normalized_phone) is True

    payload = {
        "email": email,
        "password": "securePassword123!",
        "password_confirm": "securePassword123!",
        "name": "홍길동",
        "nickname": "testuser12",
        "gender": "MALE",
        "phone_number": phone,
        "birth_date": "2000-09-09",
    }

    response = client.post(reverse("signup"), data=payload)


    assert response.status_code == 201
    assert response.json()["message"] == "회원가입이 완료되었습니다."
