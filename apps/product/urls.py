from django.urls import path

from apps.product.views.like_list_view import ProductLikeListView
from apps.product.views.like_views import ProductLikeAPIView
from apps.product.views.product_list_views import ProductListView
from apps.product.views.products_detail_view import ProductDetailAPIView
from apps.product.views.products_exchange_return_views import (
    ProductExchangeReturnAPIView,
)

urlpatterns = [
    # 좋아요
    path("like/<int:product_id>/", ProductLikeAPIView.as_view(), name="product-like"),
    path("liked/products/", ProductLikeListView.as_view(), name="product-like-list"),
    # 상품목록 조회
    path("product/", ProductListView.as_view(), name="product-list"),
    path("<int:product_id>/", ProductDetailAPIView.as_view(), name="product-detail"),
    # apps/product/urls.py
    path(
        "products/<uuid:product_exchange_id>/", ProductExchangeReturnAPIView.as_view(), name="product-exchange-return"
    ),
]
