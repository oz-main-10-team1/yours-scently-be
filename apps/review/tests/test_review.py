import uuid

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.product.models import Perfume, Product
from apps.review.models import Review

User = get_user_model()

EMAIL = f"testuser_{uuid.uuid4().hex[:6]}@example.com"
PASSWORD = "password123"
NICKNAME = f"u{uuid.uuid4().hex[:8]}"[:10]
PHONE_NUMBER = f"010{uuid.uuid4().hex[:8]}"[:11]


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email=EMAIL,
        password=PASSWORD,
        nickname=NICKNAME,
        phone_number=PHONE_NUMBER,
        is_active=True,
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    login_url = reverse("email-login")
    res = client.post(login_url, {"email": EMAIL, "password": PASSWORD}, format="json")
    token = res.json().get("access") or res.json().get("access_token")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def perfume(db):
    return Perfume.objects.create(
        name="테스트 퍼퓸",
        brand="브랜드",
        release_year=2023,
        intensity=Perfume.IntensityChoices.EAU_DE_PARFUM,
    )


@pytest.fixture
def product(db, perfume):
    return Product.objects.create(
        name="테스트 향수",
        perfume=perfume,
        volume_ml=50,
        description="테스트 설명",
        category=Product.Category.DAILY,
        price=50000,
        stock=10,
        product_img_url="https://example.com/img.jpg",
    )


@pytest.fixture
def review_payload():
    return {"content": "향이 은은하고 오래가요.", "rating": 4}


@pytest.mark.django_db
class TestReviewCreateAPI:

    def test_create_success(self, auth_client, product, review_payload):
        url = reverse("review-create", kwargs={"product_id": product.id})
        res = auth_client.post(url, data=review_payload, format="json")

        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()
        assert data["content"] == review_payload["content"]
        assert data["rating"] == review_payload["rating"]
        assert data["product_id"] == product.id

    def test_create_unauthorized(self, product, review_payload):
        url = reverse("review-create", kwargs={"product_id": product.id})
        client = APIClient()
        res = client.post(url, data=review_payload, format="json")

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_not_found(self, auth_client, review_payload):
        invalid_id = 99999
        url = reverse("review-create", kwargs={"product_id": invalid_id})
        res = auth_client.post(url, data=review_payload, format="json")

        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_create_invalid_rating(self, auth_client, product):
        url = reverse("review-create", kwargs={"product_id": product.id})
        invalid_payload = {"content": "좋아요", "rating": 6}
        res = auth_client.post(url, data=invalid_payload, format="json")

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert "rating" in res.json()
