from django.urls import path

from apps.product.views.like_views import ProductLikeAPIView

urlpatterns = [
    # 좋아요
    path("like/<int:product_id>/", ProductLikeAPIView.as_view(), name="product-like"),
]
