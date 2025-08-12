from decimal import Decimal
from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.product.models import MainAccord, Perfume, Product
from apps.recommendation.models import Recommendation, RecommendationHistory
from apps.users.models import User


@pytest.mark.django_db
def test_history_requires_auth():
    client = APIClient()
    url = reverse("recommendation-history")
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_recommendation_with_clova_and_sampling(monkeypatch):
    """
    - Clova 응답 모킹 (description/keywords 제공)
    - sample_ids 모킹으로 선택된 향수 결정
    - 응답 본문에 description/price/image_url 등 포함 확인
    - DB에 Recommendation/History 생성 확인
    """
    # 유저 & 인증
    user = User.objects.create_user(email="test@example.com", password="pass1234", nickname="테스트")
    client = APIClient()
    client.force_authenticate(user=user)

    # 키워드(메인 어코드) 준비
    warm = MainAccord.objects.create(name="포근한")
    powder = MainAccord.objects.create(name="파우더리")
    musk = MainAccord.objects.create(name="머스크")

    # 향수/상품 2개 (하나는 재고가 있는 최저가, 하나는 전부 품절)
    p1 = Perfume.objects.create(name="윈터 머스크", brand="브랜드A", release_year=2020)
    p1.main_accords.add(warm, powder, musk)
    # p1 - 품절 저가(50), 재고 있는 저가(60) -> 대표는 60.00
    Product.objects.create(
        perfume=p1,
        name="p1-품절-저가",
        description="...",
        category=Product.Category.DAILY,
        price=Decimal("50.00"),
        stock=0,
        product_img_url="https://example.com/p1_soldout.jpg",
    )
    Product.objects.create(
        perfume=p1,
        name="p1-재고-저가",
        description="...",
        category=Product.Category.DAILY,
        price=Decimal("60.00"),
        stock=10,
        product_img_url="https://example.com/p1_ok.jpg",
    )

    p2 = Perfume.objects.create(name="스윗 플로럴", brand="브랜드C", release_year=2022)
    p2.main_accords.add(warm, powder)
    # p2 - 전부 품절: 최저가 150.00 폴백
    Product.objects.create(
        perfume=p2,
        name="p2-품절-저가",
        description="...",
        category=Product.Category.DAILY,
        price=Decimal("150.00"),
        stock=0,
        product_img_url="https://example.com/p2_low.jpg",
    )
    Product.objects.create(
        perfume=p2,
        name="p2-품절-고가",
        description="...",
        category=Product.Category.DAILY,
        price=Decimal("200.00"),
        stock=0,
        product_img_url="https://example.com/p2_high.jpg",
    )

    # Clova 모킹
    def mock_call_clova_model(user_input: str) -> Dict:
        return {
            "description": "포근하고 달콤한 향을 추천합니다.",
            "keywords": ["머스크", "파우더리", "포근한"],
            "reason": "계절감 고려",
        }

    # 샘플링 모킹 (응답 고정)
    def mock_sample_ids(qs, k=5, hard_cap=20000):
        return [p1.id, p2.id]

    monkeypatch.setattr(
        "apps.recommendation.views.ai_recommendation_view.call_clova_model",
        mock_call_clova_model,
    )
    monkeypatch.setattr(
        "apps.recommendation.views.ai_recommendation_view.sample_ids",
        mock_sample_ids,
    )

    # 호출
    url = reverse("ai-recommend")
    resp = client.post(url, {"text": "따뜻하고 포근한 향 좋아요"}, format="json")
    assert resp.status_code == status.HTTP_201_CREATED

    data = resp.json()
    assert data["description"] == "포근하고 달콤한 향을 추천합니다."
    assert data["reason"] == "계절감 고려"
    assert len(data["recommendations"]) == 2

    # p1: 재고 있는 최저가 60.00 선택
    r1 = next(item for item in data["recommendations"] if item["perfume"]["name"] == "윈터 머스크")
    assert r1["perfume"]["price"] == 60.0
    assert r1["perfume"]["image_url"] == "https://example.com/p1_ok.jpg"

    # p2: 전부 품절 → 전체 최저가 150.00 선택
    r2 = next(item for item in data["recommendations"] if item["perfume"]["name"] == "스윗 플로럴")
    assert r2["perfume"]["price"] == 150.0
    assert r2["perfume"]["image_url"] == "https://example.com/p2_low.jpg"

    # DB 생성 확인
    assert Recommendation.objects.count() == 1
    assert RecommendationHistory.objects.count() == 2


@pytest.mark.django_db
def test_recommendation_history_list_view_flattened():
    """
    - Recommendation + RecommendationHistory를 리스트로 반환
    - Serializer의 get_perfume 정책(재고>0 최저가 → 폴백) 검증
    """
    user = User.objects.create_user(email="u2@example.com", password="pass1234", nickname="유저2")
    client = APIClient()
    client.force_authenticate(user=user)

    # 향수/상품 준비
    a = Perfume.objects.create(name="기본향수", brand="DefaultBrand", release_year=2021)
    # 기본향수: 상품 없음 → price/image_url = None
    b = Perfume.objects.create(name="윈터 머스크", brand="브랜드A", release_year=2020)
    Product.objects.create(
        perfume=b,
        name="b-재고-저가",
        description="...",
        category=Product.Category.DAILY,
        price=Decimal("80.00"),
        stock=5,
        product_img_url="https://example.com/b_ok.jpg",
    )

    # 추천/이력 생성
    rec = Recommendation.objects.create(
        user=user,
        type=Recommendation.Type.AI,
        description="당신이 선택한 따뜻하고 포근한...",
        reason="계절감 고려",
        context="머스크, 파우더리, 포근한",
    )
    RecommendationHistory.objects.bulk_create(
        [
            RecommendationHistory(recommendation=rec, perfume=a),  # 상품 없음
            RecommendationHistory(recommendation=rec, perfume=b),  # 재고 있는 최저가 존재
        ]
    )

    url = reverse("recommendation-history")
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK

    body = resp.json()
    assert "results" in body and len(body["results"]) >= 1

    result = body["results"][0]
    assert result["id"] == rec.id
    assert result["type"] == "ai"
    assert result["description"].startswith("당신이 선택한 따뜻하고 포근한")
    assert result["reason"] == "계절감 고려"
    assert result["context"] == "머스크, 파우더리, 포근한"
    assert "histories" in result and len(result["histories"]) == 2

    # a: 상품 없음
    h_a = next(h for h in result["histories"] if h["perfume"]["name"] == "기본향수")
    assert h_a["perfume"]["price"] is None
    assert h_a["perfume"]["image_url"] is None

    # b: 재고 있는 최저가 선택
    h_b = next(h for h in result["histories"] if h["perfume"]["name"] == "윈터 머스크")
    assert h_b["perfume"]["price"] == 80.0
    assert h_b["perfume"]["image_url"] == "https://example.com/b_ok.jpg"
