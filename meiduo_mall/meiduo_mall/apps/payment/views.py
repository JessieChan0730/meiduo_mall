import os

from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from orders.models import OrderInfo
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from alipay import AliPay
from rest_framework.request import Request

from payment.models import Payment


# Create your views here.
class PayMentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        user = request.user
        try:
            order_model = OrderInfo.objects.get(order_id=order_id, user=user,
                                                status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response({'message': '订单有误'}, status=status.HTTP_400_BAD_REQUEST)
        # 读取公钥,私钥内容
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"), 'r',
                  encoding='UTF-8') as f:
            app_private_key_string = f.read()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "keys/alpay_public_key.pem"), 'r',
                  encoding='UTF-8') as f:
            alipay_public_key_string = f.read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order_model.total_amount),  # 支付的金额
            subject="美多商城%s" % order_id,  # 标题
            return_url="http://www.meiduo.site:8080/pay_success.html",  # 支付成功回调界面
        )
        # 拼接完成网页链接并且返回
        alipay_url = settings.ALIPAY_URL + "?" + order_string
        return Response({'alipay_url': alipay_url})


class PaymentStatusView(APIView):
    """
    支付结果
    """

    def put(self, request: Request) -> Response:
        queryDict = request.query_params
        data = queryDict.dict()
        sign = data.pop('sign')
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"), 'r',
                  encoding='UTF-8') as f:
            app_private_key_string = f.read()
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "keys/alpay_public_key.pem"), 'r',
                  encoding='UTF-8') as f:
            alipay_public_key_string = f.read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        # 利用公钥进行验证
        success = alipay.verify(data, sign)
        if success:
            # 获取美多商城的订单号
            order_id = data.get('out_trade_no')
            # 获取支付宝的交易号
            trade_id = data.get('trade_no')
            # 绑定两个编号到数据库
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            # 修改订单状态
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])

        else:
            return Response({'message': '非法请求'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'trade_id': trade_id
        })
