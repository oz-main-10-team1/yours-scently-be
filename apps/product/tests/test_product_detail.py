import pytest
from rest_framework.test import APIClient

from apps.product.models import Perfume, Product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_product_detail_api_shows_correct_product_info_success(api_client):
    perfume = Perfume.objects.create(
        name="Some Perfume Name",
        brand="BrandName",
        release_year=2024,
        intensity=Perfume.IntensityChoices.EAU_DE_PARFUM,
    )
    product = Product.objects.create(
        perfume=perfume,
        volume_ml=100,
        name="Some Perfume Name 100ml",
        description="Description here",
        category="perfume",
        price=72000.00,
        stock=35,
        product_img_url="https://cdn.example.com/product15.jpg",
    )
    url = f"/api/v1/products/{product.id}/"
    response = api_client.get(url)

    assert response.status_code == 200

    response_data = response.data.get("data")
    assert response_data is not None
    assert response_data["name"] == product.name
    assert response_data["description"] == product.description
    assert float(response_data["price"]) == float(product.price)


@pytest.mark.django_db
def test_product_detail_api_failed(api_client):
    invalid_product_id = 123412112
    url = f"/api/v1/products/{invalid_product_id}/"
    response = api_client.get(url)

    assert response.status_code == 404
