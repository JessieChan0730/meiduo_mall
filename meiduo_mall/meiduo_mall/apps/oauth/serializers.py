from rest_framework import serializers
from django.core.cache import caches

from oauth.models import OAuthQQUser
from oauth.utils import check_save_user_token
from users.models import User


class QQAuthUserSerializer(serializers.Serializer):
    # mobile  password sms_code access_token
    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs: dict):
        # 解密openid
        access_token = attrs.pop('access_token')
        openid = check_save_user_token(access_token)
        if openid is None:
            raise serializers.ValidationError('openid无效')
        attrs['openid'] = openid
        # 验证验证码
        cache = caches['verify_codes']
        mobile = attrs['mobile']
        real_sms_code = cache.get(f'sms_{mobile}')
        if real_sms_code is None or int(attrs['sms_code']) != real_sms_code:
            raise serializers.ValidationError('验证码错误')
        # 手机号验证用户
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoseNotExist:
            pass
        else:
            if user.check_password(attrs['password']) is False:
                raise serializers.ValidationError('密码错误')
            else:
                attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        if user is None:
            user = User(
                username=validated_data.get('mobile'),
                mobile=validated_data.get('mobile')
            )
            user.set_password(validated_data.get('password'))
            user.save()
        OAuthQQUser.objects.create(
            openid=validated_data.get('openid'),
            user=user
        )
        return user
