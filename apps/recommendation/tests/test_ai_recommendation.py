from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.product.models import Perfume, Product
from apps.recommendation.models import Recommendation, RecommendationHistory
from apps.users.models import User


@pytest.mark.django_db
def test_create_recommendation_with_clova_mock(monkeypatch):
    user = User.objects.create_user(email="test@example.com", password="testpass123", nickname="테스트")
    client = APIClient()
    client.force_authenticate(user=user)

    perfume = Perfume.objects.create(name="테스트향수", brand="테스트브랜드", release_year=2020)

    product = Product.objects.create(
        perfume=perfume,
        name="테스트상품",
        description="테스트 상품 설명입니다.",
        category=Product.Category.DAILY,
        price=Decimal("100.00"),
        stock=10,
    )

    def mock_call_clova_model(user_input):
        return {
            "description": "포근하고 달콤한 향을 추천합니다.",
            "perfume_ids": [perfume.id],
            "keywords": ["머스크", "파우더리", "포근한"],
        }

    monkeypatch.setattr("apps.recommendation.views.ai_recommendation_view.call_clova_model", mock_call_clova_model)

    url = reverse("ai-recommend")
    payload = {"text": "달콤하고 따뜻한 향이 좋아요"}
    response = client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "recommendation_id" in data
    assert data["description"] == "포근하고 달콤한 향을 추천합니다."
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["perfume"]["name"] == "테스트향수"

    assert Recommendation.objects.count() == 1
    assert RecommendationHistory.objects.count() == 1
