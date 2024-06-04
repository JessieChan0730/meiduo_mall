from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    path('categories/<int:category_id>/skus/', views.SKUListView.as_view())
]
router = DefaultRouter()
router.register('skus/search', views.SKUSearchViewSet, basename='skus_search')
urlpatterns += router.urls
