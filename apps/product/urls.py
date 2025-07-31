from django.urls import path

from apps.product.views.like_views import LikeFalseAPIView, LikeTrueAPIView

urlpatterns = [
    # 좋아요
    path("like/<int:product_id>/", LikeTrueAPIView.as_view(), name="product-like"),
    path("unlike/<int:product_id>/", LikeFalseAPIView.as_view(), name="product-unlike"),
]
