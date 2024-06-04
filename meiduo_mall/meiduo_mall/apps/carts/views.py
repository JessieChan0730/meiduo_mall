from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from .seriaizers import CartSerializer, CartSKUSerializer, CartDeleteSerializer, CartSelectedAllSerializer
import pickle, base64


# Create your views here.


class CartView(APIView):
    # 重新验证方法,直接pass,延后认证时期
    def perform_authentication(self, request):

        pass

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')
        try:
            user = request.user
        except:
            user = None
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        # 用户登录
        if user and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()  # 创建管道
            pl.hincrby(f'cart_{user.id}', sku_id, count)
            if selected:  # 判断当前商品是否勾选
                pl.sadd(f'selected_{user.id}', sku_id)
            pl.execute()
            # return Response(serializer.data, status=status.HTTP_201_CREATED)

        # 用户没有登录
        else:
            cart_str = request.COOKIES.get('cart')
            # 购物车中存在数据
            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_bytes)
            # 匿名用户第一次添加数据
            else:
                cart_dict = {}
            #  增量
            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 设置为cookies
            cart_bytes = pickle.dumps(cart_dict)
            cart_str_bytes = base64.b64encode(cart_bytes)
            cart_str = cart_str_bytes.decode()
            response.set_cookie('cart', cart_str)

        return response

    def get(self, request):
        try:
            user = request.user
        except:
            user = None

        # 用户登录
        if user and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            cart_redis_dict: dict = redis_conn.hgetall(f'cart_{user.id}')
            selected: set = redis_conn.smembers(f'selected_{user.id}')
            # 将从redis 中取出来的数据变为和cookies一样的数据格式
            cart_dict = {}
            for sku_id_bytes, count_bytes in cart_redis_dict.items():
                cart_dict[int(sku_id_bytes)] = {
                    'count': int(count_bytes),
                    'selected': sku_id_bytes in selected
                }
        else:
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_bytes)
            else:
                return Response({'message': '没有购物车数据'}, status=status.HTTP_400_BAD_REQUEST)
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        for sku in skus:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']
        serializer = CartSKUSerializer(skus, many=True)
        return Response(serializer.data)

    def put(self, request):
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')
        response = Response(serializer.data)
        try:
            user = request.user
        except:
            user = None

        # 用户登录
        if user and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hset(f'cart_{user.id}', sku_id, count)
            if selected:
                pl.sadd(f'selected_{user.id}', sku_id)
            else:
                pl.srem(f'selected_{user.id}', sku_id)
            pl.execute()
        # 用户未登录
        else:
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return Response({
                    'message': '没有获取到cookies',
                }, status=status.HTTP_400_BAD_REQUEST)
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('cart', cart_str)
        return response

    def delete(self, request):
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        response = Response(status=status.HTTP_204_NO_CONTENT)
        try:
            user = request.user
        except:
            user = None
        # 登录
        if user and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hdel(f'cart_{user.id}', sku_id)
            pl.srem(f'selected_{user.id}', user.id, sku_id)
            pl.execute()
        # 未登录
        else:
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return Response({
                    'message': '没有获取到cookies',
                }, status=status.HTTP_400_BAD_REQUEST)
            if sku_id in cart_dict:
                del cart_dict[sku_id]
            # cookies中还有商品
            if len(cart_dict.keys()):
                cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

                response.set_cookie('cart', cart_str)
            # 如果cookies没有商品
            else:
                response.delete_cookie('cart')
        return response


class CartSelectAllView(APIView):
    def perform_authentication(self, request):
        pass

    def put(self, request):
        serializer = CartSelectedAllSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.validated_data.get('selected')
        response = Response(serializer.data)
        try:
            user = request.user
        except:
            user = None
        # 登录
        if user and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            cart_redis_dict: dict = redis_conn.hgetall(f'cart_{user.id}')
            sku_ids = cart_redis_dict.keys()
            if selected:
                redis_conn.sadd(f'selected_{user.id}', *sku_ids)
            else:
                redis_conn.srem(f'selected_{user.id}', *sku_ids)
        # 未登录
        else:
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return Response({
                    'message': '没有获取到cookies',
                }, status=status.HTTP_400_BAD_REQUEST)
            for sku_id in cart_dict:
                cart_dict[sku_id]['selected'] = selected
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('cart', cart_str)
        return response
