# 项目笔记

## 注意事项:

1. Django 3.0 版本无法使用 djangoframework-jwt，使用

```pycon
   path('authorizations/', obtain_jwt_token)
```

视图获取token会产生如下错误:

```pycon
ImportError: cannot import name ‘ugettext_lazy‘ from ‘django.utils.translation‘
```

解决方案如下：
> * 修改源代码，将其中的导包路径换为

```pycon
from django.utils.translation import gettext_lazy as _
```

> * 降低Django版本为Django==2.2.6 （不建议）
> * 使用 djangorestframework-simplejwt

```pycon
pip install djangorestframework-simplejwt
```

2. itsdangerous库中删除了TimedJSONWebSignatureSerializer类  
   解决办法如下:

> 使用 TimedSerializer类

```pycon
from django.conf import settings
from itsdangerous import TimedSerializer as Serializer

def generate_save_user_token(openid):
    """
    生成保存用户数据的token
    :param openid: 用户的openid
    :return: token
    """
    serializer = Serializer(settings.SECRET_KEY)
    data = {'openid': openid}
    token = serializer.dumps(data)
    return token.decode()

```

> 使用使用authlib库

```pycon
from authlib.jose import jwt, JoseError

def generate_token(user, operation, **kwargs):
    """生成用于邮箱验证的JWT（json web token）"""
    # 签名算法
    header = {'alg': 'HS256'}
    # 用于签名的密钥
    key = current_app.config['SECRET_KEY']
    # 待签名的数据负载
    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)

    return jwt.encode(header=header, payload=data, key=key)


def validate_token(user, token, operation):
    """用于验证用户注册和用户修改密码或邮箱的token, 并完成相应的确认操作"""
    key = current_app.config['SECRET_KEY']

    try:
        data = jwt.decode(token, key)
        print(data)
    except JoseError:
        return False
    ... # 其他字段确认
    return True
```

3. FastDFS 客户端推荐使用`py3Fdfs`库

```pycon
https://www.cnblogs.com/xcsg/p/11371091.html
https://blog.csdn.net/zy_whynot/article/details/113842879
```

docker run -dti --network=host --name storage -e TRACKER_SERVER=192.168.63.60:22122 -v /var/fdfs/storage:/var/fdfs
delron/fastdfs storage

4. windows下无法使用django-crontab,推荐使用 django-apschedule ,然后在Linux环境下切换为 django-crontab  
   https://blog.csdn.net/qq_42774234/article/details/122562830  
   https://cloud.tencent.com/developer/article/1585026


5. django3不再支持xadmin,建议使用`Simple UI`

```pycon
pip install django-simpleui
```

6. windows下不支持直接安装的uwsgi,请将项目转移到linux下安装

```pycon
pip install uwsgi
```

文档地址: 
https://newpanjing.github.io/simpleui_docs/config.html

## 项目测试环境启动

1. 数据库迁移

```pycon
python .\manage.py migrate
```

2. 项目启动

```pycon
python .\manage.py runserver
```

3. celery启动

```pycon
celery -A  celery_tasks.main   worker -l info -P eventlet (windows添加此参数)
```

4. 定时器启动

```pycon
python .\manage.py runapscheduler    
```

5. 安装依赖

```pycon
cd  meiduo_mall
pip install -r requirements.txtd
```
## 接BY设计，联系方式如下:
```commandline
QQ: 1595216569 2403428097 
```