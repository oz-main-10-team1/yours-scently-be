from django.urls import path

from apps.recommendation.views.purpose_recommendation_view import (
    ProductBannerByCategoryView,
)

urlpatterns = [
    path("banner/<str:category>/", ProductBannerByCategoryView.as_view(), name="product-banner-by-category"),
]
