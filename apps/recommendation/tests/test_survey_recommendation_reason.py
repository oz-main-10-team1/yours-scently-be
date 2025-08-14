from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.product.models import MainAccord, Note, Perfume, Product

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


@pytest.fixture
def test_perfume_with_notes(db):
    # 노트 생성
    rose_note = Note.objects.create(name="rose", type="top")
    musk_note = Note.objects.create(name="musk", type="base")
    jasmine_note = Note.objects.create(name="jasmine", type="middle")

    # 어코드 생성
    floral_accord = MainAccord.objects.create(name="floral")
    rose_accord = MainAccord.objects.create(name="rose")

    perfume = Perfume.objects.create(
        name="Romantic Rose", brand="TestBrand", release_year=2023, intensity="eau_de_toilette", embedding=[0.5] * 512
    )

    perfume.top_notes.add(rose_note)
    perfume.middle_notes.add(jasmine_note)
    perfume.base_notes.add(musk_note)
    perfume.main_accords.add(floral_accord, rose_accord)

    # Product 생성
    Product.objects.create(
        perfume=perfume,
        volume_ml=50,
        name="Romantic Rose 50ml",
        description="로맨틱한 향수",
        category="Special",
        price=120000,
        stock=5,
    )

    return perfume


@pytest.mark.django_db
def test_recommendation_reason_api_success(api_client, authenticated_user, test_perfume_with_notes):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("recommendation-reason")
    payload = {
        "perfume_id": test_perfume_with_notes.id,
        "mood": "로맨틱하고 부드러운 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "특별한 날",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 200
    data = response.json()

    assert "perfume_id" in data
    assert "reason" in data
    assert data["perfume_id"] == test_perfume_with_notes.id
    assert isinstance(data["reason"], str)
    assert len(data["reason"]) > 0

    reason = data["reason"]
    assert "rose" in reason or "musk" in reason
    assert "향수입니다" in reason


# 노트 매칭이 제대로 되는지 테스트
@pytest.mark.django_db
def test_recommendation_reason_api_note_matching(api_client, authenticated_user, test_perfume_with_notes):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("recommendation-reason")
    payload = {
        "perfume_id": test_perfume_with_notes.id,
        "mood": "로맨틱하고 부드러운 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "특별한 날",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 200
    data = response.json()

    # 매칭된 노트가 사유에 포함되는지 확인
    reason = data["reason"]
    # "사랑스러운" 키워드에 rose가 매핑되고, 향수에 rose가 있으므로 포함되어야 함
    assert "rose" in reason.lower()


@pytest.mark.django_db
def test_recommendation_reason_api_perfume_not_found(api_client, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("recommendation-reason")
    payload = {
        "perfume_id": 99999,
        "mood": "상쾌한 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "데일리용",
        "keyword": "시크한",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 404
    data = response.json()
    assert "message" in data
    assert "찾을 수 없습니다" in data["message"]


# 잘못된 요청에 대한 응답
@pytest.mark.django_db
def test_recommendation_reason_api_invalid_data(api_client, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("recommendation-reason")
    payload = {
        "perfume_id": "invalid",
        "mood": "존재하지않는분위기",
        "intensity": "적당한 향이 좋아요",
        "usage": "데일리용",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 400
    data = response.json()
    assert "perfume_id" in data or "mood" in data


@pytest.mark.django_db
def test_recommendation_reason_api_missing_fields(api_client, authenticated_user):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("recommendation-reason")
    payload = {
        "perfume_id": 1,
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 400
    data = response.json()
    missing_fields = ["mood", "intensity", "usage", "keyword"]
    for field in missing_fields:
        assert field in data


# 매칭되는 노트가 없을 때도 적절한 사유 제공
@pytest.mark.django_db
def test_recommendation_reason_api_no_matching_notes(api_client, authenticated_user):
    different_note = Note.objects.create(name="bergamot", type="top")
    woody_accord = MainAccord.objects.create(name="woody")

    perfume = Perfume.objects.create(
        name="Different Scent", brand="TestBrand", release_year=2023, intensity="eau_de_toilette", embedding=[0.5] * 512
    )
    perfume.top_notes.add(different_note)
    perfume.main_accords.add(woody_accord)

    Product.objects.create(
        perfume=perfume,
        volume_ml=50,
        name="Different Scent 50ml",
        description="다른 향수",
        category="Daily",
        price=80000,
        stock=3,
    )

    api_client.force_authenticate(user=authenticated_user)

    url = reverse("recommendation-reason")
    payload = {
        "perfume_id": perfume.id,
        "mood": "상쾌한 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "데일리용",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 200
    data = response.json()

    reason = data["reason"]
    assert len(reason) > 0
    assert "향수입니다" in reason or "어울리는" in reason


# 응답 데이터 상세검증
@pytest.mark.django_db
def test_recommendation_reason_response_structure(api_client, authenticated_user, test_perfume_with_notes):
    api_client.force_authenticate(user=authenticated_user)

    url = reverse("recommendation-reason")
    payload = {
        "perfume_id": test_perfume_with_notes.id,
        "mood": "로맨틱하고 부드러운 느낌",
        "intensity": "적당한 향이 좋아요",
        "usage": "특별한 날",
        "keyword": "사랑스러운",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 200
    data = response.json()

    # 응답 구조 검증
    required_fields = ["perfume_id", "reason"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"

    # 타입 검증
    assert isinstance(data["perfume_id"], int)
    assert isinstance(data["reason"], str)
    assert data["perfume_id"] == test_perfume_with_notes.id

    # 사유 품질 검증
    reason = data["reason"]
    assert len(reason) >= 10
    assert reason.endswith("향수입니다.") or "어울리는" in reason
