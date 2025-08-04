import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestMyProfileUpdate:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            email="test@example.com", password="strongpassword123!", nickname="new_name", phone_number="01000000000"
        )

    @pytest.fixture
    def client_with_login(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_patch_profile_update_success(self, client_with_login, user):
        url = reverse("my-profile-update")  # 안전하게 name 사용
        payload = {"nickname": "new_name", "phone_number": "01012345678"}

        response = client_with_login.patch(url, data=payload, format="json")

        assert response.status_code == 200
        assert response.data["nickname"] == "new_name"
        assert response.data["phone_number"] == "01012345678"

        user.refresh_from_db()
        assert user.nickname == "new_name"
        assert user.phone_number == "01012345678"

    def test_patch_profile_partial_update(self, client_with_login, user):
        url = reverse("my-profile-update")
        payload = {"nickname": "part_name"}

        response = client_with_login.patch(url, data=payload, format="json")

        assert response.status_code == 200
        assert response.data["nickname"] == "part_name"

        user.refresh_from_db()
        assert user.nickname == "part_name"
        assert user.phone_number == "01000000000"  # unchanged

    def test_patch_profile_unauthenticated(self):
        client = APIClient()
        url = reverse("my-profile-update")
        payload = {"nickname": "part_name"}

        response = client.patch(url, data=payload, format="json")

        assert response.status_code == 401
