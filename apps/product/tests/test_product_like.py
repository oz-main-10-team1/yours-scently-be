import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.product.models import Product
from apps.product.models.like import Like
from apps.users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(email="user@test.com", password="test1234", nickname="user1", is_active=True)


@pytest.fixture
def product(db):
    return Product.objects.create(
        name="테스트향수",
        brand="테스트브랜드",
        description="은은하고 부드러운 향",
        category=Product.Category.DAILY,
        price=19900,
        stock=10,
        product_img_url="https://example.com/image.jpg",
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    login_url = reverse("email-login")
    res = client.post(login_url, {"email": user.email, "password": "test1234"})
    assert res.status_code == 200
    token = res.data["access_token"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.mark.django_db
def test_product_like_post_success(auth_client, product):
    url = reverse("product-like", kwargs={"product_id": product.id})  # URL name 확인 필요
    response = auth_client.post(url)

    assert response.status_code == 200
    assert response.data["liked"] is True

    like = Like.objects.get(product=product)
    assert like.is_liked is True


@pytest.mark.django_db
def test_product_like_delete_success(auth_client, product, user):
    # 미리 찜해놓기
    Like.objects.create(user=user, product=product, is_liked=True)

    url = reverse("product-like", kwargs={"product_id": product.id})
    response = auth_client.delete(url)

    assert response.status_code == 200
    assert response.data["liked"] is False

    like = Like.objects.get(user=user, product=product)
    assert like.is_liked is False

@pytest.mark.django_db
def test_product_like_delete_fail_no_like_record(auth_client, product):
    url = reverse("product-like", kwargs={"product_id": product.id})
    response = auth_client.delete(url)

    assert response.status_code == 400
    assert response.data["detail"] == "찜한 내역이 없습니다."


@pytest.mark.django_db
def test_product_like_delete_fail_already_unliked(auth_client, product, user):
    Like.objects.create(user=user, product=product, is_liked=False)

    url = reverse("product-like", kwargs={"product_id": product.id})
    response = auth_client.delete(url)

    assert response.status_code == 400
    assert response.data["detail"] == "이미 찜하지 않은 상태입니다."