import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.product.models import Perfume, Product
from apps.review.models import Review
from apps.users.models import User


@pytest.mark.django_db
class TestReviewSummaryAPI:
    def setup_method(self):
        self.client = APIClient()

        self.user = User.objects.create_user(email="test@example.com", password="testpassword")
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

        self.review = Review.objects.create(
            user=self.user,
            product=self.product,
            content="정말 좋아요!",
            rating=5,
        )

    def test_review_summary_success(self):
        url = reverse("review-summary", kwargs={"product_id": self.product.id})
        res = self.client.post(url)

        assert res.status_code == 200
        data = res.json()
        assert data["product_id"] == self.product.id
        assert data["review_count"] == 1
        assert data["average_rating"] == 5
        assert data["latest_reviews"][0]["content"] == self.review.content

    def test_review_summary_not_found(self):
        url = reverse("review-summary", kwargs={"product_id": 999999})
        res = self.client.post(url)

        assert res.status_code == 404
        assert str(res.data["detail"]) == "해당 향수 상품을 찾을 수 없습니다."
