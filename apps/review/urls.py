from django.urls import path

from apps.review.views.review import ReviewCreateAPIView
from apps.review.views.review_summary import ReviewSummaryAPIView

urlpatterns = [
    path("scents/<int:product_id>/reviews/", ReviewCreateAPIView.as_view(), name="review-create"),
    path("scents/<int:product_id>/review-summary/", ReviewSummaryAPIView.as_view(), name="review-summary"),
]
