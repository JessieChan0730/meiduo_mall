# 开发环境
"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import datetime
import os
from pathlib import Path
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 添加导包路径
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-jz$+!&jy&g0t(tjjk9j0q1w#ms@@ul=zll4gx$6o52(w78bg2h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'www.meiduo.site']

# Application definition
# 注册应用
INSTALLED_APPS = [
    'simpleui',  # 注意这里',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_apscheduler',
    'django_crontab',  # 定时任务
    # 因为前面添加了导包的路径
    'rest_framework_simplejwt',
    # 下面这个app用于刷新refresh_token后，将旧的加到到blacklist时使用
    'haystack',
    'rest_framework_simplejwt.token_blacklist',
    'ckeditor',
    'ckeditor_uploader',
    'users',
    'verifications',
    'oauth',
    'areas',
    'goods',
    'contents',
    'carts',
    'payment',
    'orders'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'meiduo',
        'PASSWORD': 'cheng20011101',
        'USER': 'root',
        'HOST': '127.0.0.1',
        'PORT': 3306
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_codes": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "area_data": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "history": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "cart": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/5",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/meiduo.log"),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}
REST_FRAMEWORK = {
    # 分页
    'DEFAULT_PAGINATION_CLASS': 'meiduo_mall.utils.pagination.StandardResultsSetPagination',
    # 异常处理
    'EXCEPTION_HANDLER': 'meiduo_mall.utils.exceptions.exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    )
}

AUTH_USER_MODEL = 'users.User'
# 容联云相关配置
ACCOUNT_SID = '8a216da881ad97540181db86737b0837'
AUTH_TOKEN = '153550a7e97149c1aadef0117c920013'
APP_ID = '8a216da881ad97540181db8674d3083e'

# CORS
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:8080',
    'http://localhost:8080',
    'http://www.meiduo.site:8080',
    'http://www.meiduo.site'
]
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie

SIMPLE_JWT = {

    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=7),  # Access Token的有效期
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=7),  # Refresh Token的有效期
    # 是否自动刷新Refresh Token
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',  # 加密算法
    "TOKEN_OBTAIN_SERIALIZER": "users.serializers.MyTokenObtainPairSerializer",
}

# 修改Django认证后端类
AUTHENTICATION_BACKENDS = [
    'users.utils.UsernameMobileAuthBackend',
]

QQ_CLIENT_ID = '101474184'
QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'

# 发送邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# smpt服务地址
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25  # 端口默认都是25不需要修改
# 发送邮件的邮箱，需要配置开通SMTP
EMAIL_HOST_USER = '2403428097@qq.com'
# 在邮箱中设置的客户端授权密码
# 此处的EMAIL_HOST_PASSWORD是用QQ邮箱授权码登录
EMAIL_HOST_PASSWORD = 'quwsarmhooceeaeg'
# 收件人看到的发件人
EMAIL_FROM = '2403428097@qq.com'

# DRF扩展 用于缓存drf数据
REST_FRAMEWORK_EXTENSIONS = {
    # 缓存时间
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,
    # 缓存存储
    'DEFAULT_USE_CACHE': 'area_data'
}

# 激活重写存储文件引擎方法
DEFAULT_FILE_STORAGE = 'meiduo_mall.utils.fastdfs.fastdfs.FastDfsStroage'
# 图片存阿里云的地址
FDAS_URL = 'http://192.168.63.60:8888/'

# 存进阿里云服务器里因为没有后缀(jpg/png)，图z片连接要放进 img 标签里才能显示
# <img src="http://39.106.64.101:8888/group1/M00/00/00/rBHmx10A9JmAVEKNAABf71XWOL06003319" alt=""># 配置 Fastdfs 配置文件
FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')

# 富文本编辑器ckeditor配置
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',  # 工具条功能
        'height': 300,  # 编辑器高度
        # 'width': 300,  # 编辑器宽
    },
}
CKEDITOR_UPLOAD_PATH = ''  # 上传图片保存路径，使用了FastDFS，所以此处设为''

# 生成的静态html文件保存目录
GENERATED_STATIC_HTML_FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_web')

# 定时任务
CRONJOBS = [
    # 每5分钟执行一次生成主页静态文件
    (
        '*/5 * * * *', 'contents.crons.generate_static_index_html',
        f'>> {os.path.abspath(os.path.join(os.getcwd(), "../.."))}' + "\\logs\\crontab.log")
]

ALIPAY_APPID = '9021000132658014'
ALIPAY_DEBUG = True
ALIPAY_URL = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'

# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'whoosh_index')
    },
}
# 当添加、修改、删除数据时，⾃动⽣成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_web/static')
