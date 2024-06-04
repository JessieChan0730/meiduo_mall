import re
import time

from authlib.jose import jwt, JoseError
from django.conf import settings
from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    try:
        if re.match('^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user


# 验证邮箱
def generate_email_token(data: dict, expire_time):
    """生成用于邮箱验证的JWT（json web token）"""
    # 签名算法
    header = {'alg': 'HS256'}
    expiration_date = int(time.time()) + expire_time
    # 用于签名的密钥
    key = settings.SECRET_KEY
    # 待签名的数据负载
    payload = {'exp': expiration_date}
    payload.update(**data)

    return jwt.encode(header=header, payload=payload, key=key)


def check_email_token(token):
    """用于验证用户注册和用户修改密码或邮箱的token, 并完成相应的确认操作"""
    key = settings.SECRET_KEY
    try:
        data = jwt.decode(token, key)
        # 超时报错
        if time.time() > int(data.pop('exp')):
            raise JoseError
    except JoseError:
        return None
    else:
        return data
