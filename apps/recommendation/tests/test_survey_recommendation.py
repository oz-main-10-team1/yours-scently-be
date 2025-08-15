import json
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.product.models import MainAccord, Note, Perfume, Product
from apps.recommendation.models import Recommendation, RecommendationHistory
from apps.recommendation.views.survey_recommendation_view import (
    PerfumeRecommendationView,
)

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
def api_client():
    return APIClient()


# 더미데이터 생성
@pytest.fixture
def perfume_test_data(db):
    # 노트 생성 (type 필드 포함)
    top_note = Note.objects.create(name="rose", type="top")
    mid_note = Note.objects.create(name="jasmine", type="middle")
    base_note = Note.objects.create(name="amber", type="base")

    # MainAccord 생성
    fresh_accord = MainAccord.objects.create(name="fresh")
    green_accord = MainAccord.objects.create(name="green")

    # Perfume 생성
    perfume = Perfume.objects.create(
        name="Light Breeze",
        brand="Acme",
        release_year=2023,
        intensity="eau_de_toilette",  # 실제 choices 값으로 수정
    )

    perfume.top_notes.add(top_note)
    perfume.middle_notes.add(mid_note)
    perfume.base_notes.add(base_note)
    perfume.main_accords.add(fresh_accord, green_accord)

    # Product 연결
    Product.objects.create(
        perfume=perfume,
        volume_ml=50,
        name="Light Breeze 50ml",
        description="상쾌한 향수",
        category="Daily",
        price=89000,
        stock=10,
    )

    return perfume


# 여러 향수 중 점수 비교 테스트
@pytest.fixture
def multiple_perfumes(db):
    # 노트 생성
    rose_note = Note.objects.create(name="rose", type="top")
    jasmine_note = Note.objects.create(name="jasmine", type="middle")
    peony_note = Note.objects.create(name="peony", type="middle")

    # MainAccord 생성
    fresh_accord = MainAccord.objects.create(name="fresh")
    green_accord = MainAccord.objects.create(name="green")

    # 첫 번째 향수
    perfume1 = Perfume.objects.create(
        name="Average Match",
        brand="Brand1",
        release_year=2023,
        intensity="eau_de_toilette",
    )
    perfume1.top_notes.add(rose_note)
    perfume1.main_accords.add(fresh_accord)
    Product.objects.create(
        perfume=perfume1,
        volume_ml=50,
        name="Average Match 50ml",
        description="평범한 향수",
        category="Daily",
        price=79000,
        stock=5,
    )

    # 두 번째 향수
    perfume2 = Perfume.objects.create(
        name="Perfect Match",
        brand="Brand2",
        release_year=2023,
        intensity="eau_de_toilette",
    )
    perfume2.top_notes.add(rose_note)
    perfume2.middle_notes.add(jasmine_note, peony_note)
    perfume2.main_accords.add(fresh_accord, green_accord)
    Product.objects.create(
        perfume=perfume2,
        volume_ml=50,
        name="Perfect Match 50ml",
        description="완벽한 향수",
        category="Daily",
        price=99000,
        stock=3,
    )

    return perfume1, perfume2


# 기본 향수 추천 API 테스트
@pytest.mark.django_db
def test_perfume_recommendation_api(api_client, perfume_test_data, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("survey-recommendation")
    payload = {
        "mood": "상쾌한 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "데일리용",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["name"] == perfume_test_data.name
    assert data["brand"] == perfume_test_data.brand
    assert data["intensity"] == "eau_de_toilette"
    assert isinstance(data["main_accords"], list)
    assert "fresh" in data["main_accords"]
    assert "green" in data["main_accords"]
    assert "score" in data
    assert isinstance(data["score"], float)
    assert 0.0 <= data["score"] <= 1.0  # 코사인 유사도 범위


# 매핑과 전혀 맞지 않는 경우 404 응답 확인
@pytest.mark.django_db
def test_perfume_recommendation_no_match(api_client, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("survey-recommendation")
    payload = {
        "mood": "상쾌한 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "데일리용",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "조건에 맞는 향수를 찾을 수 없습니다." in response.json().get("message", "")


# 잘못된 요청 데이터 검증
@pytest.mark.django_db
def test_perfume_recommendation_invalid_data(api_client, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("survey-recommendation")

    # 필수 필드 누락
    payload = {
        "mood": "상쾌한 느낌",
        # "intensity": 누락
        "usage": "데일리용",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")
    assert response.status_code == 400
    response_data = response.json()
    assert "intensity" in response_data
    assert isinstance(response_data["intensity"], list)
    assert len(response_data["intensity"]) > 0

    error_message = response_data["intensity"][0]
    assert "required" in error_message.lower() or "필수" in error_message


# 여러 후보 중 최고 점수 선택 확인
@pytest.mark.django_db
def test_perfume_recommendation_best_score(api_client, multiple_perfumes, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    perfume1, perfume2 = multiple_perfumes

    url = reverse("survey-recommendation")
    payload = {
        "mood": "상쾌한 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "데일리용",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")
    assert response.status_code == 200
    data = response.json()

    assert data["name"] in ["Average Match", "Perfect Match"]
    assert data["score"] > 0.0
    assert isinstance(data["score"], float)

    assert "id" in data
    assert "brand" in data
    assert data["intensity"] == "eau_de_toilette"
    assert "fresh" in data["main_accords"]


# 완전 매칭이 안될 때 점진적 완화 로직 테스트
@pytest.mark.django_db
def test_perfume_recommendation_relaxed_matching(api_client, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    # 부분적으로만 매칭되는 향수 생성
    rose_note = Note.objects.create(name="rose", type="top")
    fresh_accord = MainAccord.objects.create(name="fresh")

    perfume = Perfume.objects.create(
        name="Relaxed Match",
        brand="TestBrand",
        release_year=2023,
        intensity="parfum",  # intensity 불일치
    )
    perfume.top_notes.add(rose_note)  # keyword 일치 (rose)
    perfume.main_accords.add(fresh_accord)  # mood 일치 (fresh)

    # category 불일치하는 Product
    Product.objects.create(
        perfume=perfume,
        volume_ml=50,
        name="Relaxed Match 50ml",
        description="테스트 향수",
        category="Special",
        price=120000,
        stock=2,
    )

    url = reverse("survey-recommendation")
    payload = {
        "mood": "상쾌한 느낌",  # 일치 (fresh)
        "intensity": "적당한 향이 좋아요",  # 불일치 (parfum vs eau_de_toilette)
        "usage": "데일리용",  # 불일치 (Special vs Daily)
        "keyword": "사랑스러운",  # 일치 (rose)
    }

    response = api_client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Relaxed Match"


# 응답 데이터 구조 상세 검증
@pytest.mark.django_db
def test_perfume_recommendation_response_structure(api_client, perfume_test_data, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("survey-recommendation")
    payload = {
        "mood": "상쾌한 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "데일리용",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    required_fields = ["id", "name", "brand", "intensity", "main_accords", "score"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"

    assert isinstance(data["id"], int)
    assert isinstance(data["name"], str)
    assert isinstance(data["brand"], str)
    assert isinstance(data["intensity"], str)
    assert isinstance(data["main_accords"], list)
    assert isinstance(data["score"], float)
    assert 0.0 <= data["score"] <= 1.0

    valid_intensities = ["parfum", "eau_de_parfum", "eau_de_toilette", "eau_de_cologne", "eau_fraiche"]
    assert data["intensity"] in valid_intensities


# 이력 저장 기능 테스트
@pytest.mark.django_db
def test_perfume_recommendation_saves_history(api_client, perfume_test_data, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    initial_count = Recommendation.objects.filter(user=authenticated_user).count()

    url = reverse("survey-recommendation")
    payload = {
        "mood": "상쾌한 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "데일리용",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # 응답에 history_id가 포함되어야 함
    assert "history_id" in data
    assert isinstance(data["history_id"], int)

    # 이력이 실제로 저장되었는지 확인
    final_count = Recommendation.objects.filter(user=authenticated_user).count()
    assert final_count == initial_count + 1

    # 저장된 이력 내용 검증
    recommendation = Recommendation.objects.get(id=data["history_id"])
    assert recommendation.user == authenticated_user
    assert recommendation.type == "survey"

    # context에 설문 데이터가 JSON으로 저장되었는지 확인
    context = json.loads(recommendation.context)
    assert context["mood"] == "상쾌한 느낌"
    assert context["intensity"] == "적당한 향이 좋아요"
    assert context["usage"] == "데일리용"
    assert context["keyword"] == "사랑스러운"

    history = RecommendationHistory.objects.filter(recommendation=recommendation).first()
    assert history is not None
    assert history.perfume == perfume_test_data
    assert history.similarity_score == data["score"]


# 이력 저장 실패해도 추천 결과는 정상 반환되는지 확인
@pytest.mark.django_db
def test_perfume_recommendation_history_failure_still_returns_result(
    api_client, perfume_test_data, authenticated_user, mocker
):
    api_client.force_authenticate(user=authenticated_user)

    # 이력 저장 함수에서 예외 발생하도록 모킹
    mock_create_history = mocker.patch(
        "apps.recommendation.views.survey_recommendation_view.PerfumeRecommendationView._create_recommendation_history",
        side_effect=Exception("Database error"),
    )

    url = reverse("survey-recommendation")
    payload = {
        "mood": "상쾌한 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "데일리용",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")

    # 이력 저장 실패에도 불구하고 추천 결과는 정상 반환
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["name"] == perfume_test_data.name
    assert data["brand"] == perfume_test_data.brand
    assert "score" in data

    # history_id는 없어야 함 (저장 실패했으므로)
    assert "history_id" not in data

    # 이력 저장 함수가 호출되었는지 확인
    mock_create_history.assert_called_once()


# 비인증 사용자는 이력이 저장되지 않음을 확인
@pytest.mark.django_db
def test_unauthenticated_user_no_history_saved(api_client, perfume_test_data):
    url = reverse("survey-recommendation")
    payload = {
        "mood": "상쾌한 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "데일리용",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# 기존 테스트 중 응답 구조 검증 테스트 업데이트
@pytest.mark.django_db
def test_perfume_recommendation_response_structure_with_history(api_client, perfume_test_data, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("survey-recommendation")
    payload = {
        "mood": "상쾌한 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "데일리용",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # 기존 필수 필드들
    required_fields = ["id", "name", "brand", "intensity", "main_accords", "score"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"

    # 새로 추가된 필드
    assert "history_id" in data
    assert isinstance(data["history_id"], int)

    # 기존 검증 로직들
    assert isinstance(data["id"], int)
    assert isinstance(data["name"], str)
    assert isinstance(data["brand"], str)
    assert isinstance(data["intensity"], str)
    assert isinstance(data["main_accords"], list)
    assert isinstance(data["score"], float)
    assert 0.0 <= data["score"] <= 1.0

    valid_intensities = ["parfum", "eau_de_parfum", "eau_de_toilette", "eau_de_cologne", "eau_fraiche"]
    assert data["intensity"] in valid_intensities
