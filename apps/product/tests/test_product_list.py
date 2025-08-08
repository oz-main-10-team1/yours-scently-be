from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.product.models import Perfume, Product

User = get_user_model()


class ProductListAPITest(APITestCase):
    # 사용자 생성 및 JWT 토큰 발급
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="testuser@testuser.com", password="testpass123", is_active=True)
        cls.access_token = str(RefreshToken.for_user(cls.user).access_token)

        # 향수 하나 생성 (모든 상품에 공통적으로 사용)
        cls.perfume = Perfume.objects.create(
            name="테스트 향수",
            brand="테스트 브랜드",
            release_year=2022,
            intensity="eau_de_parfum",
        )

        # 상품 15개 생성 (페이지당 10개 가정)
        products = [
            Product(
                name=f"상품 {i}",
                perfume=cls.perfume,
                description="테스트 향수입니다.",
                category="Daily",
                price=10000 + i,
                stock=20,
                volume_ml=50,
                product_img_url=f"https://example.com/images/product_{i}.jpg",
            )
            for i in range(15)
        ]
        Product.objects.bulk_create(products)

    def setUp(self):
        self.access_token = self.__class__.access_token

    def _auth_headers(self):
        return {"HTTP_AUTHORIZATION": f"Bearer {self.access_token}"}

    def test_product_list_pagination_success(self):
        url = reverse("product-list")  # 페이지네이션 적용된 API
        response = self.client.get(url, **self._auth_headers())

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIsInstance(response.data["results"], list)

        # 기본 페이지 사이즈(예: 10개) 확인
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(response.data["count"], 15)
        self.assertIsNotNone(response.data["next"])  # 다음 페이지 있어야 함

    def test_product_list_second_page(self):
        """상품 목록 두 번째 페이지 조회"""
        url = reverse("product-list") + "?limit=10&offset=10"
        response = self.client.get(url, **self._auth_headers())

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 5)

    def test_product_list_unauthenticated(self):
        """인증 없이 요청할 경우 401 응답을 반환한다."""
        url = reverse("product-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)
        self.assertIn("자격 인증데이터", str(response.data["detail"]))
