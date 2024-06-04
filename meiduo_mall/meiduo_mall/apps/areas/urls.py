from django.urls import path, include

from . import views
from rest_framework.routers import DefaultRouter

app_name = 'areas'
urlpatterns = [
    # path('', views.AreaListView.as_view(), name='index'),
    # path('<int:pk>/', views.AreaDetailView.as_view(), name='detail'),
]
router = DefaultRouter()
router.register('areas', views.AreaViewSet, basename='area')  # 是图集中没有指定query_set,那么此时一定需要传递basename
urlpatterns += router.urls
