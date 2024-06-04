from ronglian_sms_sdk import SmsSDK
from django.conf import settings


def send_message(phone, message):
    sdk = SmsSDK(settings.ACCOUNT_SID, settings.AUTH_TOKEN,
                 settings.APP_ID)
    sdk.sendMessage('1', mobile=phone, datas=(message, 5))
