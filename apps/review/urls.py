from django.urls import path

from apps.review.views.review import ReviewCreateAPIView

urlpatterns = [
    path("scents/<int:product_id>/reviews/", ReviewCreateAPIView.as_view(), name="review-create"),
]
