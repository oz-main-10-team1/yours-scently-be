# apps/products/tests.py

from django.test import TestCase
from .models import Perfume
import datetime

class TestPerfumeListView(TestCase):  # ✅ 클래스 이름이 Test 로 시작해야 함

    @classmethod
    def setUpTestData(cls):
        for i in range(5):
            Perfume.objects.create(
                name=f"Perfume {i}",
                brand="Test Brand",
                price=10000 + i,
                image_url="http://example.com/image.png",
                description="Test description",
                release_date=datetime.date(2024, 1, 1) - datetime.timedelta(days=i)
            )

    def test_perfume_count(self):  # ✅ 메서드 이름이 test_로 시작해야 함
        self.assertEqual(Perfume.objects.count(), 5)
