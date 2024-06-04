import random
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import caches
import logging
from rest_framework import status
from . import constants
from celery_tasks.sms.tasks import send_sms_code

logger = logging.getLogger('django')


# Create your views here.

class SMSCode(APIView):
    def get(self, request, mobile):
        cache = caches['verify_codes']
        send_flag = cache.get(f'send_flag_{mobile}')
        logger.info(send_flag)
        if send_flag:
            return Response({
                'message': '手机频繁发送短信'
            }, status=status.HTTP_400_BAD_REQUEST)

        code = random.randint(1111, 9999)
        logger.info(code)
        # 缓存
        cache.set(f'sms_{mobile}', code, constants.SMS_CODE_REDIS_EXPIRES)
        cache.set(f'send_flag_{mobile}', 1, constants.SEND_SMS_CODE_INTERVAL)
        send_sms_code.delay(mobile, code)
        # 发送短信
        # send_message(mobile, code)
        return Response({
            'message': 'ok'
        })
