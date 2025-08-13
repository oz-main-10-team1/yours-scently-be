import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.product.models import Perfume, Product
from apps.review.models import Review
from apps.users.models import User


@pytest.mark.django_db
class TestUserReviewsAPI:
    def setup_method(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="me@example.com",
            password="testpass123!",
            name="테스터",
            nickname="tester_me",
            phone_number="01012345678",
            is_active=True,
        )

        self.client.force_authenticate(user=self.user)

        self.perfume = Perfume.objects.create(
            name="테스트 퍼퓸",
            brand="테스트 브랜드",
            release_year=2025,
            intensity="eau_de_parfum",
        )
        self.product = Product.objects.create(
            name="테스트 상품",
            description="설명입니다",
            category="DAILY",
            price=10000,
            stock=100,
            perfume=self.perfume,
        )

    def _make_review(self, idx: int, rating: int = 5):
        return Review.objects.create(
            user=self.user,
            product=self.product,
            content=f"리뷰 {idx}",
            rating=rating,
        )

    def test_user_reviews_success(self):
        for i in range(12):
            self._make_review(i)

        url = reverse("user-reviews")
        res = self.client.get(url, {"page": 2, "size": 5})

        assert res.status_code == 200
        data = res.json()
        assert data["page"] == 2
        assert data["size"] == 5
        assert data["total"] == 12
        assert len(data["reviews"]) == 5
        item = data["reviews"][0]
        assert {"review_id", "product_id", "product_name", "content", "rating", "created_at"} <= set(item.keys())

    def test_user_reviews_unauthorized(self):
        self.client.force_authenticate(user=None)
        url = reverse("user-reviews")
        res = self.client.get(url)

        assert res.status_code == 401

    def test_user_reviews_no_reviews(self):
        url = reverse("user-reviews")
        res = self.client.get(url)

        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert len(data["reviews"]) == 0

    def test_user_reviews_invalid_query_params(self):
        url = reverse("user-reviews")
        res = self.client.get(url, {"page": "abc", "size": "xyz"})
        assert res.status_code == 400
        assert "page와 size는 정수여야 합니다." in res.json().get("detail", "")

    def test_user_reviews_out_of_range(self):
        for i in range(3):
            self._make_review(i)

        url = reverse("user-reviews")
        res = self.client.get(url, {"page": 9, "size": 10})
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 3
        assert len(data["reviews"]) == 0
