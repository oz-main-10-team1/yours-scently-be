from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/', include('apps.product.urls')),
    path('products/', ProductListView.as_view(), name='product-list'),

    ]