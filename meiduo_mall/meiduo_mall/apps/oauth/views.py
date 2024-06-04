from rest_framework.response import Response
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from rest_framework import status

from oauth.models import OAuthQQUser
from .serializers import QQAuthUserSerializer
from .utils import generate_save_user_token
from rest_framework_simplejwt.tokens import RefreshToken
from carts.utils import merge_cart_cookie_to_redis


# Create your views here.

class QQOauthURLView(APIView):
    def get(self, request):
        next = request.query_params.get('next') or '/'
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)
        # 返回回调链接
        login_url = oauth.get_qq_url()
        return Response({
            'login_url': login_url
        })


class QQAuthUserView(APIView):
    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            return Response({'message': 'QQ服务器异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # 使用openid查询该QQ用户是否在美多商城中绑定过用户
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # openid没有绑定用户
            # 加密openid给客户端
            access_token_openid = generate_save_user_token(openid)
            return Response({'access_token': access_token_openid})
        else:
            # 如果openid已绑定美多商城用户，直接生成JWT token，并返回
            # jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            # 获取oauth_user关联的user
            user = oauth_user.user
            # payload = jwt_payload_handler(user)
            # token = jwt_encode_handler(payload)
            refresh = RefreshToken.for_user(user)

            response = Response({
                'token': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username
            })
            # 合并购物车数据
            merge_cart_cookie_to_redis(request, user, response)

            return response

    def post(self, request):
        serializer = QQAuthUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        response = Response({
            'token': str(refresh.access_token),
            'username': user.username,
            'user_id': user.pk
        })
        # 合并购物车数据
        merge_cart_cookie_to_redis(request, user, response)
        return response
