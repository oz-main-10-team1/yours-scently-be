from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.users.models import User, Withdrawal
from apps.users.tasks import delete_expired_withdrawn_users


@pytest.fixture
def active_user(db, django_user_model):
    return django_user_model.objects.create_user(
        email="test@example.com", password="testpass123", nickname="테스트유저", is_active=True
    )


@pytest.fixture
def auth_client(active_user):
    client = APIClient()
    login_url = reverse("email-login")  # your login URL name
    response = client.post(login_url, {"email": active_user.email, "password": "testpass123"})
    assert response.status_code == 200, response.data
    token = response.data.get("access_token")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.mark.django_db
def test_withdrawal_success(auth_client, active_user):
    url = reverse("user-withdrawal")  # your withdrawal URL name
    data = {"reason": "NOT_SATISFIED", "detail": "추천이 이상해요"}

    response = auth_client.post(url, data)

    assert response.status_code == 200
    active_user.refresh_from_db()
    assert not active_user.is_active

    withdrawal = Withdrawal.objects.get(user=active_user)
    assert withdrawal.reason == data["reason"]
    assert withdrawal.reason_detail == data["detail"]
    assert withdrawal.due_date == timezone.now().date() + timedelta(days=14)


@pytest.mark.django_db
def test_duplicate_withdrawal(auth_client, active_user):
    Withdrawal.objects.create(
        user=active_user,
        reason="ETC",
        reason_detail="중복 테스트",
        due_date=timezone.now().date() + timedelta(days=14),
    )

    url = reverse("user-withdrawal")
    data = {"reason": "ETC", "detail": "중복 요청"}

    response = auth_client.post(url, data)

    assert response.status_code == 400
    assert response.data["detail"] == "이미 탈퇴 요청된 사용자입니다."


@pytest.mark.django_db
def test_login_after_withdrawal(client, active_user):
    active_user.is_active = False
    active_user.save()

    login_url = reverse("email-login")
    response = client.post(login_url, {"email": active_user.email, "password": "testpass123"})

    assert response.status_code == 400
    assert response.data["non_field_errors"][0] == "이메일 또는 비밀번호가 올바르지 않습니다."


@pytest.mark.django_db
def test_celery_task_deletes_expired_user():
    user = User.objects.create_user(
        email="expired@example.com",
        password="testpass123",
        nickname="탈퇴예정자",
        is_active=False,
    )

    Withdrawal.objects.create(
        user=user,
        reason="ETC",
        reason_detail="14일 지남",
        due_date=timezone.now().date() - timedelta(days=1),
    )

    delete_expired_withdrawn_users()

    # 유저가 삭제되었는지 확인
    with pytest.raises(User.DoesNotExist):
        User.objects.get(id=user.id)

    # Withdrawal도 삭제되었는지 확인
    assert not Withdrawal.objects.filter(user_id=user.id).exists()
