import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    cart_str: str = request.COOKIES.get('cart')
    if cart_str is None:
        return
    cart_dict: dict = pickle.loads(base64.b64decode(cart_str.encode()))
    redis_conn = get_redis_connection('cart')
    pl = redis_conn.pipeline()
    for sku_id in cart_dict:
        pl.hset(f'cart_{user.id}', sku_id, cart_dict[sku_id]['count'])
        if cart_dict[sku_id]['selected']:
            pl.sadd(f'selected_{user.id}', sku_id)
    pl.execute()
    response.delete_cookie('cart')
