import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.product.models import Product


@pytest.mark.django_db
class TestProductBannerByCategory:
    @pytest.fixture
    def sample_products(self):
        return Product.objects.bulk_create(
            [
                Product(
                    name=f"운동향수 {i}",
                    brand="테스트브랜드",
                    description="설명입니다.",
                    category=Product.Category.OUTDOOR,
                    price=10000 + i * 1000,
                    stock=10,
                    product_img_url=f"https://example.com/image{i}.jpg",
                )
                for i in range(7)
            ]
        )

    def test_banner_api_success(self, sample_products):
        client = APIClient()
        url = reverse("product-banner-by-category", kwargs={"category": "Outdoor"})

        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert 1 <= len(response.data) <= 5

        for product in response.data:
            assert "id" in product
            assert "name" in product
            assert "brand" in product
            assert "price" in product
            assert "product_img_url" in product

    def test_banner_api_invalid_category(self):
        client = APIClient()
        url = reverse("product-banner-by-category", kwargs={"category": "InvalidCategory"})

        response = client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
