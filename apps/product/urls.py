from django.urls import path

from apps.product.views.like_list_view import ProductLikeListView
from apps.product.views.like_views import ProductLikeAPIView
from apps.product.views.product_views import ProductListView
from apps.product.views.products_detail_views import ProductDetailView

urlpatterns = [
    # 좋아요
    path("like/<int:product_id>/", ProductLikeAPIView.as_view(), name="product-like"),
    path("liked/products/", ProductLikeListView.as_view(), name="product-like-list"),
    # 상품목록 조회
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
]
