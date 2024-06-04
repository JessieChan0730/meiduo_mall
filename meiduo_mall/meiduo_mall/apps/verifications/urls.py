from django.urls import path, re_path
from . import views

app_name = 'verifications'
urlpatterns = [
    # 发短信
    re_path(r'^(?P<mobile>1[3-9]\d{9})/$', views.SMSCode.as_view(),name='smscode')
]
