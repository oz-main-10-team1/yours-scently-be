import pytest
from apps.users.models import User
from apps.users.serializers.my_page import MyPageSerializer, MyPerfumeSerializer
from apps.product.models.perfume import Perfume


@pytest.mark.django_db
def test_myperfume_serializer_minimal_fields_no_mainaccord():
    p = Perfume.objects.create(
        name="Test Perfume",
        brand="Test Brand",
        release_year=2025,
    )

    data = MyPerfumeSerializer(p).data

    for key in ["id", "name", "brand", "intensity"]:
        assert key in data


@pytest.mark.django_db
def test_mypage_serializer_returns_user_with_perfumes_without_mainaccord_dependency():
    user = User.objects.create_user(
        email="tester@example.com",
        password="testpass123!",
    )

    perfume = Perfume.objects.create(
        name="Serializer Check",
        brand="Brand X",
        release_year=2025,
    )
    user.perfumes.add(perfume)

    data = MyPageSerializer(user).data

    for key in ["id", "email", "created_at", "perfumes"]:
        assert key in data

    assert isinstance(data["perfumes"], list)
    assert len(data["perfumes"]) == 1

    p0 = data["perfumes"][0]
    for key in ["id", "name", "brand", "intensity"]:
        assert key in p0
