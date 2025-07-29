# apps/products/urls.py
from django.urls import path
from .views import PerfumeListView

urlpatterns = [
    path('e-commerce/perfumes/', PerfumeListView.as_view(), name='perfume-list'),
]