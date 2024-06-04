from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    token_obtain_pair
)
from . import views

app_name = 'users'
urlpatterns = [
    path('register/', views.UserView.as_view(), name='register'),
    path('users/<str:username>/', views.UserCountView.as_view(), name='is_user_exists'),
    path('mobile/<str:mobile>/', views.MobileCountView.as_view(), name='is_mobile_exists'),
    # 继承重写验证类,用于完成合并购物车功能
    path('authorizations/', views.UserAuthorizeView.as_view()),
    path('authorizations/refresh/', TokenRefreshView.as_view()),
    path('user/', views.UserDetailView.as_view()),
    path('email/', views.EmailView.as_view()),
    path('emails/verification/', views.EmailVerifyView.as_view()),
    path('browse_histories/', views.UserBrowserHistoryView.as_view())
]

router = routers.DefaultRouter()
router.register(r'addresses', views.AddressViewSet, basename='addresses')

urlpatterns += router.urls
