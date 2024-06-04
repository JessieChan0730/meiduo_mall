from django_redis import get_redis_connection
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from goods.models import SKU
from .serializers import UserAddressSerializer, AddressTitleSerializer
from users.serializers import CreateUserSerializer, UserDetailSerializer, MyTokenObtainPairSerializer, EmailSerializer, \
    UserBrowserHistorySerializer, SKUSerializer
from .models import User, Address
from .utils import check_email_token
from rest_framework.mixins import UpdateModelMixin
from rest_framework_simplejwt.views import TokenObtainPairView
from carts.utils import merge_cart_cookie_to_redis
from .models import User


# Create your views here.

class UserView(CreateAPIView):
    serializer_class = CreateUserSerializer


class UserCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data)


class UserDetailView(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmailVerifyView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        data = check_email_token(token)
        if data is None:
            # token出现问题
            return Response({'message': '请重新验证'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=data.get('user_id'))
            user.email_active = True
            user.save()
            return Response({'message': 'ok'})
        except Exception as e:
            # 查询不到用户
            return Response({'message': '激活失败'}, status=status.HTTP_400_BAD_REQUEST)


class AddressViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAddressSerializer

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 20,
            'addresses': serializer.data,
        })

    def create(self, request):
        user = request.user
        count = Address.objects.filter(user=user).count()
        if count >= 20:
            return Response({'message': '数量上限'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)


class UserBrowserHistoryView(CreateAPIView):
    """用户商品浏览记录"""

    serializer_class = UserBrowserHistorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        redis_conn = get_redis_connection('history')
        sku_ids = redis_conn.lrange(f'history_{request.user.id}', 0, -1)
        sku_list = []
        # SKU.objects.filter(id__in=sku_ids)
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)
        serializer = SKUSerializer(sku_list, many=True)
        return Response(serializer.data)


class UserAuthorizeView(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = User.objects.get(id=serializer.validated_data.get('user_id'))
        except TokenError as e:
            raise InvalidToken(e.args[0])
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        # 合并购物车
        merge_cart_cookie_to_redis(request, user, response)
        return response
