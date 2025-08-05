from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class TChangePasswordTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="originalpass123")
        self.url = reverse("update-change-password")
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        data = {"new_password": "newsecurepass123", "new_password_confirm": "newsecurepass123"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "비밀번호가 변경되었습니다.")

    def test_passwords_do_not_match(self):
        data = {"new_password": "newsecurepass123", "new_password_confirm": "differentpass123"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("비밀번호가 일치하지 않습니다.", str(response.data))

    def test_password_too_short(self):
        data = {"new_password": "short", "new_password_confirm": "short"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This password is too short", str(response.data))  # Django 기본 메시지

    def test_same_as_current_password(self):
        data = {
            "new_password": "originalpass123",
        }
