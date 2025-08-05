import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.mark.django_db
class TestNicknameDuplicateCheckAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test1@example.com",
            password="testpass123",
            nickname="기존닉네임",
            phone_number="01011112222",  # 고유하게 지정
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("update-check-nickname")

    def test_nickname_not_duplicate(self):
        response = self.client.post(self.url, {"nickname": "새닉네임"})
        assert response.status_code == 200
        assert response.data["is_duplicate"] is False

    def test_nickname_duplicate(self):
        User.objects.create_user(
            email="test2@example.com",
            password="testpass456",
            nickname="중복닉네임",
            phone_number="01022223333",  # 다른 번호
        )
        response = self.client.post(self.url, {"nickname": "중복닉네임"})
        assert response.status_code == 200
        assert response.data["is_duplicate"] is True

    def test_nickname_same_as_own(self):
        response = self.client.post(self.url, {"nickname": "기존닉네임"})
        assert response.status_code == 200
        assert response.data["is_duplicate"] is False

    def test_nickname_field_missing(self):
        response = self.client.post(self.url, {})
        assert response.status_code == 400
        assert "nickname" in response.data
        assert response.data["nickname"][0] == "nickname 필드는 필수입니다."

    def test_nickname_too_long(self):
        response = self.client.post(self.url, {"nickname": "111열글자이상닉네임"})
        assert response.status_code == 400
        assert "nickname" in response.data
