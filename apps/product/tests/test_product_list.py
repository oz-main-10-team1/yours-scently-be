from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.product.models import Product

User = get_user_model()


class ProductListAPITest(APITestCase):
    def setUp(self):
        # 사용자 생성 및 JWT 토큰 발급
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.access_token = str(RefreshToken.for_user(self.user).access_token)

        # 상품 15개 생성 (페이지당 10개 가정)
        for i in range(15):
            Product.objects.create(
                name=f"상품 {i}",
                brand="브랜드",
                description="테스트 향수입니다.",
                category="STANDARD",
                price=10000 + i,
                stock=20,
                product_img_url=f"https://example.com/images/product_{i}.jpg",
                release_date=date(2024, 1, 1),
            )

    def _auth_headers(self):
        """JWT 인증 헤더 생성"""
        return {"HTTP_AUTHORIZATION": f"Bearer {self.access_token}"}

    def test_product_list_pagination_success(self):
        """상품 목록을 무한스크롤 형식으로 페이지네이션 조회한다."""
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
        url = reverse("product-list") + "?page=2"
        response = self.client.get(url, **self._auth_headers())

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 5)  # 남은 5개

    def test_product_list_unauthenticated(self):
        """인증 없이 요청할 경우 401 응답을 반환한다."""
        url = reverse("product-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.data)
        self.assertIn("credentials were not provided", str(response.data["detail"]).lower())
