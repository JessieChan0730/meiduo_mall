from django.utils.datetime_safe import datetime
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from decimal import Decimal
from django_redis import get_redis_connection
from django.db import transaction


class CartSKUSerializer(serializers.ModelSerializer):
    """
        购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='商品的购买数量')

    class Meta:
        model = SKU
        fields = ['id', 'name', 'default_image_url', 'price', 'count']


class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)


class CommitOrderSerializer(serializers.ModelSerializer):
    """开始事务,四张表同时操作"""

    class Meta:
        model = OrderInfo
        fields = ['address', 'pay_method', 'order_id']
        read_only_fields = ['order_id']
        extra_kwargs = {
            'address': {'write_only': True},
            'pay_method': {'write_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        redis_conn = get_redis_connection('cart')
        address = validated_data.get('address')
        pay_method = validated_data.get('pay_method')
        status = (OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH'] else
                  OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        with transaction.atomic():  # 手动开启事务
            save_point = transaction.savepoint()  # 保存回滚点
            try:
                order_info = OrderInfo.objects.create(
                    order_id=datetime.now().strftime('%Y%m%d%H%M%S') + '%09d' % user.id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0.00'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=status
                )

                cart_dict_redis = redis_conn.hgetall(f'cart_{user.id}')
                selected_ids = redis_conn.smembers(f'selected_{user.id}')
                print(selected_ids)
                for sku_id_bytes in selected_ids:
                    while True:  # 多次下单机会
                        sku = SKU.objects.get(id=sku_id_bytes)
                        # 购物车商品的数量恩
                        buy_count = int(cart_dict_redis[sku_id_bytes])
                        origin_sales = sku.sales
                        origin_stock = sku.stock
                        if buy_count > origin_stock:
                            raise serializers.ValidationError('库存不足')
                        # 计算对应的库存和销量数据
                        new_sales = origin_sales + buy_count
                        new_stock = origin_stock - buy_count
                        # sku.sales = new_sales
                        # sku.stock = new_stock
                        # sku.save()
                        result = SKU.objects.filter(stock=origin_stock, id=sku_id_bytes).update(stock=new_stock,
                                                                                                sales=new_sales)
                        if result == 0:
                            continue  # 下单失败

                        # 修改SPU销量
                        spu = sku.goods
                        spu.sales += buy_count
                        spu.save()

                        # 保存订单商品信息
                        OrderGoods.objects.create(
                            order=order_info,
                            sku=sku,
                            count=buy_count,
                            price=sku.price
                        )
                        # 计算总数量和总价
                        order_info.total_count += buy_count
                        order_info.total_amount += (sku.price * buy_count)
                        break  # 下单成功

                # 加入邮费和保存订单信息
                order_info.total_amount += order_info.freight
                order_info.save()
            except Exception as e:
                # 进行回滚
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('库存不足')
            else:
                # 中间没有出现问题则提交事务
                transaction.savepoint_commit(save_point)  # 中间没有出现问题提交事务
            # 清除购物车中已经购买的商品
            pl = redis_conn.pipeline()
            pl.hdel(f'cart_{user.id}', *selected_ids)
            pl.srem(f'selected_{user.id}', *selected_ids)
            pl.execute()
            # 返回订单模型对象
        return order_info
