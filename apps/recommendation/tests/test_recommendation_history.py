import json
from datetime import date, datetime, timezone

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.product.models import MainAccord, Note, Perfume, Product
from apps.recommendation.models import Recommendation, RecommendationHistory

User = get_user_model()


@pytest.fixture
def authenticated_user(db):
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        name="Test User",
        nickname="testuser",
        gender="MALE",
        birth_date=date(1995, 5, 15),
        phone_number="010-1234-5678",
        is_active=True,
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email="other@example.com",
        password="testpass123",
        name="Other User",
        nickname="otheruser",
        gender="FEMALE",
        birth_date=date(1990, 3, 20),
        phone_number="010-9876-5432",
        is_active=True,
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_perfumes(db):
    # 노트 생성
    rose_note = Note.objects.create(name="rose", type="top")
    musk_note = Note.objects.create(name="musk", type="base")
    citrus_note = Note.objects.create(name="citrus", type="top")

    # 어코드 생성
    romantic_accord = MainAccord.objects.create(name="romantic")
    fresh_accord = MainAccord.objects.create(name="fresh")

    perfume1 = Perfume.objects.create(
        name="Romantic Musk",
        brand="Fragrance House",
        release_year=2023,
        intensity="eau_de_parfum",
        embedding=[0.8] * 512,
    )
    perfume1.top_notes.add(rose_note)
    perfume1.base_notes.add(musk_note)
    perfume1.main_accords.add(romantic_accord)

    Product.objects.create(
        perfume=perfume1,
        volume_ml=50,
        name="Romantic Musk 50ml",
        description="로맨틱한 향수",
        category="Special",
        price=150000,
        stock=3,
    )

    perfume2 = Perfume.objects.create(
        name="Blush Bloom", brand="Elegant Scent", release_year=2023, intensity="eau_de_toilette", embedding=[0.7] * 512
    )
    perfume2.top_notes.add(rose_note)
    perfume2.main_accords.add(romantic_accord)

    Product.objects.create(
        perfume=perfume2,
        volume_ml=30,
        name="Blush Bloom 30ml",
        description="우아한 향수",
        category="Daily",
        price=89000,
        stock=5,
    )

    return perfume1, perfume2


@pytest.fixture
def recommendation_history(authenticated_user, sample_perfumes):
    perfume1, perfume2 = sample_perfumes

    recommendation = Recommendation.objects.create(
        user=authenticated_user,
        type=Recommendation.Type.SURVEY,
        description="설문 기반 향수 추천",
        reason="사용자 설문 응답을 바탕으로 한 개인화 추천",
        context=json.dumps(
            {"mood": "로맨틱한", "intensity": "적당한 향이 좋아요", "usage": "데일리용", "keyword": "사랑스러운"},
            ensure_ascii=False,
        ),
    )

    history1 = RecommendationHistory.objects.create(
        recommendation=recommendation, perfume=perfume1, similarity_score=0.89
    )

    history2 = RecommendationHistory.objects.create(
        recommendation=recommendation, perfume=perfume2, similarity_score=0.76
    )

    return recommendation


@pytest.fixture
def multiple_recommendations(authenticated_user, sample_perfumes):
    perfume1, perfume2 = sample_perfumes

    # 첫 번째 추천 세션
    rec1 = Recommendation.objects.create(
        user=authenticated_user,
        type=Recommendation.Type.SURVEY,
        description="첫 번째 추천",
        context=json.dumps({"mood": "상쾌한", "keyword": "활기찬"}),
    )
    RecommendationHistory.objects.create(recommendation=rec1, perfume=perfume1, similarity_score=0.85)

    # 두 번째 추천 세션
    rec2 = Recommendation.objects.create(
        user=authenticated_user,
        type=Recommendation.Type.AI,
        description="AI 기반 추천",
        context=json.dumps({"preferences": "복합적"}),
    )
    RecommendationHistory.objects.create(recommendation=rec2, perfume=perfume2, similarity_score=0.92)

    return rec1, rec2


# 추천 이력 목록 조회 테스트
@pytest.mark.django_db
def test_recommendation_history_list(api_client, authenticated_user, recommendation_history):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("recommendation-history")
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    results = data["results"]
    assert len(results) == 1

    history_item = results[0]

    # 실제 응답 필드에 맞게 검증 수정
    assert "id" in history_item
    assert "type" in history_item
    assert "created_at" in history_item
    assert "histories" in history_item

    # 기본 정보 검증
    assert history_item["id"] == recommendation_history.id
    assert history_item["type"] == "survey"

    # 추천된 향수들 검증 (histories 필드)
    histories = history_item["histories"]
    assert len(histories) == 2  # 우리가 생성한 향수 2개

    # 첫 번째 향수 정보 검증
    first_history = histories[0]
    assert "perfume" in first_history
    perfume = first_history["perfume"]
    assert "name" in perfume
    assert "brand" in perfume

    # 향수 이름 확인
    perfume_names = [h["perfume"]["name"] for h in histories]
    assert "Romantic Musk" in perfume_names
    assert "Blush Bloom" in perfume_names


# 여러 추천 이력 목록 조회 테스트
@pytest.mark.django_db
def test_recommendation_history_list_multiple(api_client, authenticated_user, multiple_recommendations):
    api_client.force_authenticate(user=authenticated_user)
    rec1, rec2 = multiple_recommendations

    url = reverse("recommendation-history")
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()

    assert "results" in data
    results = data["results"]
    assert len(results) == 2

    # 실제 필드에 맞게 검증
    result_ids = [item["id"] for item in results]
    assert rec1.id in result_ids
    assert rec2.id in result_ids

    # 타입 검증
    result_types = [item["type"] for item in results]
    assert "survey" in result_types
    assert "ai" in result_types


# 추천 이력 상세 조회 테스트
@pytest.mark.django_db
def test_recommendation_history_detail(api_client, authenticated_user, recommendation_history):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("recommendation-history-detail", kwargs={"history_id": recommendation_history.id})
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()

    required_fields = ["history_id", "recommended_at", "recommendation_type", "condition", "recommended_perfumes"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}. Available fields: {list(data.keys())}"

    assert data["history_id"] == recommendation_history.id
    assert data["recommendation_type"] == "survey"

    # 조건 정보 검증 (context에서 파싱된 설문 데이터)
    condition = data["condition"]
    assert condition["mood"] == "로맨틱한"
    assert condition["intensity"] == "적당한 향이 좋아요"
    assert condition["usage"] == "데일리용"
    assert condition["keyword"] == "사랑스러운"

    # 추천 향수들 검증
    recommended_perfumes = data["recommended_perfumes"]
    assert len(recommended_perfumes) == 2

    # 향수 정보 검증
    perfume_names = [p["perfume_name"] for p in recommended_perfumes]
    assert "Romantic Musk" in perfume_names
    assert "Blush Bloom" in perfume_names


# 존재하지 않는 이력 조회 시 404
@pytest.mark.django_db
def test_recommendation_history_detail_not_found(api_client, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("recommendation-history-detail", kwargs={"history_id": 99999})
    response = api_client.get(url)

    assert response.status_code == 404


# 다른 사용자의 이력 조회 시 404 (권한 없음)
@pytest.mark.django_db
def test_recommendation_history_detail_other_user(api_client, other_user, recommendation_history):
    api_client.force_authenticate(user=other_user)

    url = reverse("recommendation-history-detail", kwargs={"history_id": recommendation_history.id})
    response = api_client.get(url)

    assert response.status_code == 404


# 추천 이력이 없는 경우 빈 목록 반환
@pytest.mark.django_db
def test_recommendation_history_empty_list(api_client, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("recommendation-history")
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 0


# 인증되지 않은 사용자의 접근 시 401 - 인증하지 않은 상태로 요청
@pytest.mark.django_db
def test_recommendation_history_unauthenticated(api_client, recommendation_history):
    # 목록 조회
    url = reverse("recommendation-history")
    response = api_client.get(url)
    assert response.status_code == 401

    # 상세 조회
    url = reverse("recommendation-history-detail", kwargs={"history_id": recommendation_history.id})
    response = api_client.get(url)
    assert response.status_code == 401


# context JSON 파싱 관련 테스트
@pytest.mark.django_db
def test_recommendation_context_parsing_fallback(api_client, authenticated_user, sample_perfumes):
    perfume1, _ = sample_perfumes

    # 잘못된 JSON context를 가진 추천 생성
    recommendation = Recommendation.objects.create(
        user=authenticated_user,
        type=Recommendation.Type.SURVEY,
        description="잘못된 컨텍스트 테스트",
        context="invalid json string",  # 잘못된 JSON
    )

    RecommendationHistory.objects.create(recommendation=recommendation, perfume=perfume1, similarity_score=0.75)

    api_client.force_authenticate(user=authenticated_user)

    url = reverse("recommendation-history-detail", kwargs={"history_id": recommendation.id})
    response = api_client.get(url)

    assert response.status_code == 200
    data = response.json()

    assert data["history_id"] == recommendation.id
    assert data["recommendation_type"] == "survey"

    # fallback 조건 검증 (JSON 파싱 실패시 기본값)
    condition = data["condition"]
    assert condition == {"mood": "", "intensity": "", "usage": "", "keyword": ""}
