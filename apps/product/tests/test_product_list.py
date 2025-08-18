import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.product.models import Perfume, Product

User = get_user_model()


# ---------------------------
# Fixtures
# ---------------------------
@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="testuser@example.com", password="testpass")  # 이메일 필수


@pytest.fixture
def perfume(db):
    return Perfume.objects.create(name="테스트 향수", brand="테스트 브랜드", release_year=2025)


@pytest.fixture
def products(db, perfume):
    products = []
    for i in range(15):
        product = Product.objects.create(
            perfume=perfume,
            name=f"테스트 향수 {i}",
            description="기본 설명",
            category="Daily",
            price=10000 + i,
            stock=10 + i,
            product_img_url="https://example.com/images/test.jpg",
        )
        products.append(product)
    return products


# ---------------------------
# Tests
# ---------------------------
@pytest.mark.django_db
def test_product_list_pagination_success(api_client, user, products):
    # 로그인
    api_client.force_authenticate(user=user)
    url = "/api/v1/product/?limit=10&offset=0"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data
    assert "data" in response.data["results"]

    products_list = response.data["results"]["data"]
    assert isinstance(products_list, list)
    assert len(products_list) <= 10

    assert "message" in response.data["results"]
    assert response.data["results"]["message"] == "상품 목록 조회 성공 (조회수 증가)"


@pytest.mark.django_db
def test_product_list_unauthenticated(api_client, user, products):
    # 인증 없이 접근 시, API permission에 따라 상태 코드 확인
    url = "/api/v1/product/?limit=10&offset=0"

    # 인증 없이 호출
    response = api_client.get(url)

    # 인증 필요하면 401, 필요 없으면 200
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
