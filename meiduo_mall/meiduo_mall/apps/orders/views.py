from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from goods.models import SKU
from decimal import Decimal
from .serializer import OrderSettlementSerializer, CommitOrderSerializer


# Create your views here.
class OrderSettlementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        redis_conn = get_redis_connection('cart')
        cart_dict_redis = redis_conn.hgetall('cart_%s' % user.id)
        selected_ids = redis_conn.smembers(f'selected_{user.id}')
        cart_dict = {}
        for sku_id_bytes in selected_ids:
            cart_dict[int(sku_id_bytes)] = int(cart_dict_redis[sku_id_bytes])
        skus = SKU.objects.filter(id__in=cart_dict.keys())
        for sku in skus:
            sku.count = cart_dict[sku.id]
        # 计算运费
        freight = Decimal('10.00')
        data_dict = {'freight': freight, 'skus': skus}
        serializer = OrderSettlementSerializer(data_dict)

        return Response(serializer.data)


class CommitOrderView(CreateAPIView):
    serializer_class = CommitOrderSerializer
    permission_classes = [IsAuthenticated]
