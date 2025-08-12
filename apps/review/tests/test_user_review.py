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

        # 유니크 제약(10자리) 충족: 010 + 7자리
        self.user = User.objects.create_user(
            email="me@example.com",
            password="testpassword",
            nickname="me_user",
            phone_number="0101234567",
        )

        self.client.force_authenticate(user=self.user)

        self.perfume = Perfume.objects.create(
            name="테스트 퍼퓸",
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

    def test_user_reviews_success(self):
        Review.objects.create(
            user=self.user,
            product=self.product,
            content="정말 좋아요!",
            rating=5,
        )
        Review.objects.create(
            user=self.user,
            product=self.product,
            content="그냥 그래요",
            rating=3,
        )

        url = reverse("user-reviews")
        res = self.client.get(url, {"page": 1, "size": 10})

        assert res.status_code == 200
        data = res.json()

        assert "reviews" in data and isinstance(data["reviews"], list)
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["total"] == 2

        first = data["reviews"][0]
        assert {"review_id", "product_id", "product_name", "content", "rating", "created_at"} <= set(
            first.keys()
        )
        assert first["product_id"] == self.product.id
        assert first["product_name"] == self.product.name

    def test_user_reviews_unauthorized(self):
        self.client.force_authenticate(user=None)
        url = reverse("user-reviews")
        res = self.client.get(url)
        assert res.status_code == 401

    def test_user_reviews_no_reviews(self):
        other = User.objects.create_user(
            email="other@example.com",
            password="testpassword",
            nickname="other_user",
            phone_number="0100000001",
        )

        self.client.force_authenticate(user=self.user)
        url = reverse("user-reviews")
        res = self.client.get(url, {"page": 1, "size": 10})

        assert res.status_code == 200
        data = res.json()

        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 10
        assert isinstance(data["reviews"], list) and len(data["reviews"]) == 0
