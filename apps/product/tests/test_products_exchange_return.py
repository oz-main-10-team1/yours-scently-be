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
    ProductExchangeSerializer,
)


@pytest.mark.django_db
class TestProductExchangeReturnAPIView:

    @pytest.fixture(autouse=True)
    def setup(self, django_user_model):
        self.client = APIClient()
        self.user = django_user_model.objects.create_user(email="testuser@example.com", password="testpass123")
        self.client.force_authenticate(user=self.user)

        # Perfume 생성
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
        # 1. 테스트에 필요한 객체들 생성
        exchange_product = Product_Exchange.objects.create(
            id=uuid.uuid4(), name="ExchPerf", description="ExchDesc", price=Decimal("10.99"), product=self.product
        )

        exchange_request = ExchangeReturnRequest.objects.create(
            request_id=uuid.uuid4(),
            type="exchange",
            status="pending",
            exchange_return=exchange_product,
            requests_reason="ReqReason1",
        )

        # 2. API 호출
        url = reverse("product-exchange-return", args=[exchange_product.id])
        response = self.client.get(url)

        # 3. 예상 데이터 생성: 뷰의 응답 구조와 동일하게 맞춥니다.
        expected_product_data = ProductExchangeSerializer(exchange_product).data
        expected_product_data["exchange_return"] = {
            "requests": [
                {
                    "request_id": str(exchange_request.request_id),
                    "type": "exchange",
                    "status": "pending",
                    "requests_reason": "ReqReason1",
                }
            ]
        }

        # 4. 검증
        assert response.status_code == status.HTTP_200_OK
        assert response.data["product"] == expected_product_data
