from celery_tasks.main import celery_app
from django.core.mail import send_mail
from django.conf import settings


@celery_app.task(name='send_email')
def send_email(to_email, verify_url):
    """
    发送激活邮件
    :param to_email: 收件人邮箱
    :param verify_url: 激活链接
    :return: None
    """
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    send_mail(subject, "", settings.EMAIL_FROM, [to_email], html_message=html_message)
