import uuid
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.product.models import Perfume, Product
from apps.product.models.products_exchange_return import (
    ExchangeReturnRequest,
    Product_Exchange,
)
from apps.product.serializers.products_exchange_return_serializers import (
    ProductExchangeSerializer
)


@pytest.mark.django_db
class TestProductExchangeReturnAPIView:

    @pytest.fixture(autouse=True)
    def setup(self, django_user_model):
        self.client = APIClient()
        self.user = django_user_model.objects.create_user(email="testuser@example.com", password="testpass123")
        self.client.force_authenticate(user=self.user)

        # Perfume 생성 (Product.perfume FK 필수 값)
        self.perfume = Perfume.objects.create(
            name="Perf1",
            brand="Brand1",
            release_year=2024,
        )

        # Product 생성
        self.product = Product.objects.create(
            volume_ml=100,
            name="Some Perfume Name 100ml",
            description="Description here",
            category="perfume",
            price=Decimal("72000.00"),
            stock=35,
            product_img_url="https://cdn.example.com/product15.jpg",
            perfume=self.perfume,
        )

    def test_success_response(self):
        self.ProductExchange = Product_Exchange.objects.create(
            id=uuid.uuid4(), name="ExchPerf", description="ExchDesc", price=Decimal("10.99"), product=self.product
        )

        self.ExchangeReturnRequest = ExchangeReturnRequest.objects.create(
            request_id=uuid.uuid4(),
            type="exchange",
            status="pending",
            exchange_return=self.ProductExchange,
            requests_reason="ReqReason1",
            # is_exchange_available, is_return_available 필드는 모델에 정의되어 있다면
            # 여기에 값을 추가해주어야 합니다.
            # 만약 ExchangeReturnRequest 모델에 이 필드들이 없다면,
            # 해당 필드가 있는 다른 모델에서 가져와야 합니다.
        )

        url = reverse("product-exchange-return", args=[self.ProductExchange.id])
        response = self.client.get(url)

        # API 응답 데이터를 JSON으로 변환합니다.
        serializer = ProductExchangeSerializer(self.ProductExchange)
        expected_product_data = serializer.data

        # API 응답의 product 필드 데이터와 직렬화된 데이터를 비교합니다.
        assert response.status_code == status.HTTP_200_OK
        assert response.data["product"] == expected_product_data
        assert len(response.data["exchange_return"]["requests"]) == 1