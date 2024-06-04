from django.urls import path

from . import views

urlpatterns = [
    # 去结算
    path('settlement/', views.OrderSettlementView.as_view()),
    path('', views.CommitOrderView.as_view())
]
