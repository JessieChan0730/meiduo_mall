from django.contrib import admin
from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token

from . import views

app_name = 'oauth'
urlpatterns = [
    path('qq/authorization/', views.QQOauthURLView.as_view()),
    path('qq/user/', views.QQAuthUserView.as_view()),
]
