from django.urls import path
from . import views

urlpatterns = [
    path('<int:order_id>/payment/', views.PayMentView.as_view()),
    path('payment/status/', views.PaymentStatusView.as_view()),
]
