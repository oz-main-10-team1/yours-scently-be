from django.urls import path

from apps.recommendation.views.ai_recommendation_view import (
    RecommendationCreateView,
    RecommendationHistoryListView,
)
from apps.recommendation.views.purpose_recommendation_view import (
    ProductBannerByCategoryView,
)

urlpatterns = [
    path("banner/<str:category>/", ProductBannerByCategoryView.as_view(), name="product-banner-by-category"),
    path("ai/", RecommendationCreateView.as_view(), name="ai-recommend"),
    path("recommendations/history/", RecommendationHistoryListView.as_view(), name="recommendation-history"),
]
