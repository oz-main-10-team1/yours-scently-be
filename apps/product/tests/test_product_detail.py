import pytest
from django.urls import reverse
from apps.product.models import Product
from rest_framework.test import APIClient

# ✅ DRF APIClient fixture 정의
@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_product_detail_api_shows_correct_product_info(api_client):
    """
    상품 상세 API가 올바른 상품 정보를 반환하는지 확인하는 테스트
    """
    # 상품 2개 생성
    product1 = Product.objects.create(
        name="Test Product 1",
        description="Description for product 1.",
        price=10.00,
        stock=100
    )
    product2 = Product.objects.create(
        name="Test Product 2",
        description="Description for product 2.",
        price=20.00,
        stock=50
    )

    # product1의 상세 정보를 요청
    url = reverse("product-detail", args=[product1.pk])
    response = api_client.get(url)

    assert response.status_code == 200

    # 응답 구조에 따라 데이터 추출
    response_data = response.data.get("data")

    assert response_data is not None
    assert response_data["name"] == product1.name
    assert response_data["description"] == product1.description
    assert float(response_data["price"]) == float(product1.price)

    # product2 정보가 섞이지 않았는지 확인
    assert response_data["name"] != product2.name
