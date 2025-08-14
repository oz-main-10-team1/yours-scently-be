from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.product.models import Product
from apps.product.models.perfume import Perfume
from apps.review.models import Review
from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create(
        email="test@example.com",
        name="테스트 사용자",
        nickname="테스터",
        gender=User.Gender.MALE,
        birth_date=date(2000, 1, 1),
        phone_number="010-1234-5678",
        is_active=True,
        role=User.Role.GENERAL,
    )


@pytest.fixture
def perfume():
    return Perfume.objects.create(
        name="테스트 향수 원액",
        brand="테스트 브랜드",
        release_year=2023,
        intensity=Perfume.IntensityChoices.EAU_DE_PARFUM,
    )


@pytest.fixture
def product(perfume):
    return Product.objects.create(
        perfume=perfume,
        name="테스트 향수",
        description="테스트용 향수입니다.",
        category=Product.Category.DAILY,
        price=Decimal("50000"),
        stock=100,
        volume_ml=50,
        product_img_url="https://example.com/image.jpg",
        views_count=0,
    )


@pytest.fixture
def reviews(user, product):
    reviews = []
    for i in range(5):
        review_number = 5 - i
        review = Review.objects.create(
            user=user,
            product=product,
            rating=(i % 5) + 1,
            content=f"테스트 리뷰 내용 {review_number}",
            created_at=timezone.now() - timezone.timedelta(days=i),
        )
        reviews.append(review)
    return reviews


@pytest.mark.django_db
class TestReviewListAPI:

    def test_get_review_list_unauthenticated(self, api_client, product):
        url = reverse("product-reviews", kwargs={"product_id": product.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "total_count" in response.data
        assert "page" in response.data
        assert "limit" in response.data
        assert "reviews" in response.data

    def test_get_review_list_authenticated(self, api_client, user, product, reviews):
        url = reverse("product-reviews", kwargs={"product_id": product.id})
        api_client.force_authenticate(user=user)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "total_count" in response.data
        assert "page" in response.data
        assert "limit" in response.data
        assert "reviews" in response.data
        assert response.data["total_count"] == 5
        assert len(response.data["reviews"]) == 5

    def test_get_review_list_pagination(self, api_client, user, product, reviews):
        url = reverse("product-reviews", kwargs={"product_id": product.id})
        api_client.force_authenticate(user=user)
        response = api_client.get(f"{url}?page=1&limit=2")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_count"] == 5
        assert response.data["page"] == 1
        assert response.data["limit"] == 2
        assert len(response.data["reviews"]) == 2

    def test_get_review_list_product_not_found(self, api_client, user):
        url = reverse("product-reviews", kwargs={"product_id": 9999})
        api_client.force_authenticate(user=user)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_review_data_structure(self, api_client, user, product, reviews):
        url = reverse("product-reviews", kwargs={"product_id": product.id})
        api_client.force_authenticate(user=user)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        review = response.data["reviews"][0]

        assert "review_id" in review
        assert "user_nickname" in review
        assert "rating" in review
        assert "content" in review
        assert "created_at" in review

        assert review["user_nickname"] == user.nickname
        assert review["content"].startswith("테스트 리뷰 내용")
        assert isinstance(review["rating"], int)
        assert 1 <= review["rating"] <= 5
