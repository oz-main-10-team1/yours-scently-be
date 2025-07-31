import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.product.models import Like, Product
from apps.users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@test.com", password="test1234", nickname="user1", is_active=True)


@pytest.fixture
def auth_client(user):
    client = APIClient()
    login_url = reverse("email-login")
    res = client.post(login_url, {"email": user.email, "password": "test1234"})
    assert res.status_code == 200
    token = res.data["access_token"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def liked_products(user):
    p1 = Product.objects.create(
        name="샤넬 No.5",
        brand="Chanel",
        description="향수1",
        category="Daily",
        price=135000,
        stock=10,
        product_img_url="https://example.com/images/101.jpg",
    )
    p2 = Product.objects.create(
        name="딥디크 탐다오",
        brand="Diptyque",
        description="향수2",
        category="Special",
        price=158000,
        stock=10,
        product_img_url="https://example.com/images/102.jpg",
    )
    Like.objects.create(user=user, product=p1, is_liked=True)
    Like.objects.create(user=user, product=p2, is_liked=True)
    return [p1, p2]


@pytest.mark.django_db
def test_product_like_list(auth_client, liked_products):
    url = reverse("product-like-list")
    res = auth_client.get(url)

    assert res.status_code == 200
    assert res.data["count"] == 2
    assert len(res.data["results"]) == 2

    results = res.data["results"]
    assert results[0]["name"] == "딥디크 탐다오"
    assert results[1]["name"] == "샤넬 No.5"

    for item in res.data["results"]:
        assert item["is_liked"] is True
        assert "liked_at" in item
        assert "product_id" in item


@pytest.mark.django_db
def test_product_like_list_empty(auth_client):
    url = reverse("product-like-list")
    response = auth_client.get(url)

    assert response.status_code == 200
    assert response.data["count"] == 0
    assert response.data["results"] == []
