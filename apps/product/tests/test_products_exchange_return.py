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

        # Product 생성 (product_id 키워드 삭제)
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

        # exchange_return 필드에 Product_Exchange 객체 자체를 할당합니다.
        self.ExchangeReturnRequest = ExchangeReturnRequest.objects.create(
            request_id=uuid.uuid4(),
            type="exchange",
            status="pending",
            order_id="Order001",
            requests_at="2025-08-12T12:00:00Z",
            exchange_return=self.ProductExchange,
            requests_reason="ReqReason1",
        )

        url = reverse("product-exchange-return", args=[self.ProductExchange.id])
        response = self.client.get(url)

        # 이제 API 응답에 요청이 하나 포함될 것이므로 테스트가 성공합니다.
        assert len(response.data["exchange_return"]["requests"]) == 1
