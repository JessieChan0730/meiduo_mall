import re
from typing import Dict, Any

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from celery_tasks.email.tasks import send_email

from goods.models import SKU
from .models import User, Address
from django.core.cache import caches
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .utils import generate_email_token


class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='token', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow', 'token']
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, data):
        # 判断两次密码
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断短信验证码
        cache = caches['verify_codes']
        mobile = data['mobile']
        real_sms_code = cache.get(f'sms_{mobile}')
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if int(data['sms_code']) != real_sms_code:
            raise serializers.ValidationError('短信验证码错误')

        return data

    def create(self, validated_data: dict):
        """
        创建用户
        """
        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        # user = super().create(validated_data)
        # # 调用django的认证系统加密密码
        # user.set_password(validated_data['password'])
        # user.save()
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        # 保存数据
        user.save()

        # 生成token
        # jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt中叫jwt_payload_handler的函数
        # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 函数的引用用于生成JWT
        # payload = jwt_payload_handler(user)  # 根据user生成载荷部分
        # token = jwt_encode_handler(payload)  # 传递payload部分生成token
        refresh = RefreshToken.for_user(user)
        # 多添加一个token字段
        user.token = refresh.access_token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'email_active']


# 自定义token载荷数据
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)

        custom = {
            'username': self.user.username,
            'user_id': self.user.pk
        }
        data.update(**custom)
        return data

    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = user.pk
        token['username'] = user.username
        return token


class EmailSerializer(serializers.ModelSerializer):
    # 生成邮箱验证链接
    def generate_email_verify_url(self, user):
        print(user.username)
        data = {
            'user_id': user.pk,
            'email': user.email
        }
        token = generate_email_token(data, 3600).decode()
        return f'http://127.0.0.1:8080/success_verify_email.html?token={token}'

    # 重写此方法用于发送激活邮箱链接
    def update(self, instance, validated_data):
        # super(EmailSerializer, self).update(instance, validated_data)
        instance.email = validated_data.get('email')
        instance.save()
        # http://www.meiduo.site:8000/suceess_verify_email.html?token=1
        verify_url = self.generate_email_verify_url(instance)
        # 发送邮件
        send_email.delay(to_email=instance.email, verify_url=verify_url)
        return instance

    class Meta:
        model = User
        fields = ['id', 'email']
        extra_kwargs = {
            'email': {
                # 必须传递
                'required': True
            }
        }


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ['user', 'is_deleted', 'create_time', 'update_time']

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """
        保存
        """
        # 只有视图类是 GenericAPIView 或者是其子类才能使用此方法获得user对象
        validated_data['user'] = self.context['request'].user
        return Address.objects.create(**validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """

    class Meta:
        model = Address
        fields = ['title']


class UserBrowserHistorySerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label='商品sku_id', min_value=1)

    def validate_sku_id(self, value):
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('sku_id 不存在')
        return value

    def create(self, validated_data):
        sku_id = validated_data.get('sku_id')
        # 由于需要使用到列表,此时不能够使用cache
        user = self.context['request'].user

        redis_conn = get_redis_connection('history')
        # 创建redis管道
        pl = redis_conn.pipeline()
        pl.lrem(f'history_{user.id}', 0, sku_id)
        pl.lpush(f'history_{user.id}', sku_id)
        pl.ltrim(f'history_{user.id}', 0, 4)
        pl.execute()

        return validated_data


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'comments']
