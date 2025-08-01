from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from apps.product.models import Product
from datetime import date
from django.urls import reverse

User = get_user_model()

class ProductDetailAPITest(APITestCase):

    def setUp(self):
        # 테스트용 사용자 생성 및 JWT 발급
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # 테스트용 상품 생성
        self.product = Product.objects.create(
            name="로즈 가든",
            brand="플로라리아",
            description="풍부한 장미 향이 가득한 향수",
            category="SPECIAL",
            price=92000,
            stock=10,
            product_img_url="https://example.com/images/perfume122.jpg",
            release_date=date(2023, 11, 20),
        )

    def _auth_headers(self):
        """JWT 인증 헤더 반환"""
        return {"HTTP_AUTHORIZATION": f"Bearer {self.access_token}"}

    def test_product_detail_success(self):
        """✅ 정상적으로 상품 상세 정보를 조회한다."""
        url = f"/products/views/{self.product.id}/"  # 또는 reverse 사용
        response = self.client.get(url, **self._auth_headers())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.product.id)
        self.assertEqual(response.data["name"], self.product.name)
        self.assertEqual(response.data["brand"], self.product.brand)
        self.assertEqual(response.data["price"], self.product.price)

    def test_product_detail_not_found(self):
        """❌ 존재하지 않는 상품 ID 조회 시 404 반환"""
        url = "/products/views/9999/"
        response = self.client.get(url, **self._auth_headers())

        self.assertEqual(response.status_code, 404)
        # 메시지는 다국어 설정에 따라 달라질 수 있으므로 생략 or 확인
        self.assertIn("찾을 수 없습니다", str(response.data))

    def test_product_detail_unauthenticated(self):
        """❌ 인증 없이 요청 시 401 반환"""
        url = f"/products/views/{self.product.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 401)
        self.assertIn("credentials were not provided", str(response.data).lower())
