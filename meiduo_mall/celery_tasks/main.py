import os

from celery import Celery

# celery 主要文件
#  将celery与django项目融合 Linux环境下使用
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings.dev')

celery_app = Celery('meiduo')

celery_app.config_from_object('celery_tasks.config')

celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email', 'celery_tasks.html'])
