from django.urls import path

from apps.recommendation.views.ai_recommendation_view import (
    RecommendationCreateView,
    RecommendationHistoryListView,
)
from apps.recommendation.views.purpose_recommendation_view import (
    ProductBannerByCategoryView,
)
from apps.recommendation.views.recommendation_history_view import (
    RecommendationHistoryDetailView,
    SurveyRecommendationHistoryListView,
)
from apps.recommendation.views.survey_recommendation_reason_view import (
    RecommendationReasonView,
)
from apps.recommendation.views.survey_recommendation_view import (
    PerfumeRecommendationView,
)

urlpatterns = [
    path("banner/<str:category>/", ProductBannerByCategoryView.as_view(), name="product-banner-by-category"),
    path("ai/", RecommendationCreateView.as_view(), name="ai-recommend"),
    path("survey/", PerfumeRecommendationView.as_view(), name="survey-recommendation"),
    path("histories/", SurveyRecommendationHistoryListView.as_view(), name="recommendation-history"),
    path("history/<int:history_id>/", RecommendationHistoryDetailView.as_view(), name="recommendation-history-detail"),
    path("reason/", RecommendationReasonView.as_view(), name="recommendation-reason"),
]
