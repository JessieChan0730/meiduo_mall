# 此文件存储异步任务

from celery_tasks.main import celery_app

from celery_tasks.ronglianyun.sms import send_message


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, code):
    send_message(mobile, code)
