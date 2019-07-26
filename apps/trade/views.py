from django.shortcuts import render

# Create your views here.
from datetime import datetime
from django.shortcuts import redirect
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.permissions import IsOwnerOrReadOnly
from rest_framework import viewsets, mixins
from .serializers import ShoppingCartSerializers, ShoppingCartDetailSerializers, OrderSerializers, OrderDetailSerializer
from .models import ShoppingCart, OrderInfo, OrderGoods
from utils.alipay import AliPay
from FreshShop.settings import ALIPAY_KEY_PATH, PRIVATE_KEY_PATH, APP_NOTIFY_URL, APP_ID, RETURN_URL


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    list:
        购物车列表
    create:
        添加购物车
    update:
        修改购物车
    delete:
        删除购物车
    """

    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = 'goods_id'

    def perform_create(self, serializer):
        """
        商品库存的数量减少：购物车数量增加
        :param serializer:
        :return:
        """
        instance = serializer.save()
        goods = instance.goods
        goods.goods_num -= instance.nums
        goods.save()

    def perform_destroy(self, instance):
        """
        商品库存数量的增加：购物车数量的删除
        :param instance:
        :return:
        """
        goods = instance.goods
        goods.goods_num += instance.nums
        goods.save()
        instance.delete()

    def perform_update(self, serializer):
        """
        商品库存数量的改变：购物车里商品数量的改变
        :param serializer:
        :return:
        """
        existed_record = ShoppingCart.objects.get(id=serializer.instance.id)
        existed_nums = existed_record.nums
        save_record = serializer.save()
        nums = save_record.nums - existed_nums
        goods = save_record.goods
        goods.goods_num -= nums
        goods.save()

    def get_serializer_class(self):
        if self.action == 'list':
            return ShoppingCartDetailSerializers
        else:
            return ShoppingCartSerializers

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)


class OrderInfoViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, \
                       mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        订单列表
    create:
        添加订单
    destroy:
        删除订单
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = OrderSerializers

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializers

    def perform_create(self, serializer):
        order = serializer.save()

        shop_carts = ShoppingCart.objects.all()

        for shop in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop.goods
            order_goods.goods_num = shop.nums
            order_goods.order = order
            order_goods.save()

            shop.delete()

        return order


class AliPayView(APIView):
    """
    支付宝的支付接口
    """
    def get(self, request):
        """
        处理支付宝的return_url
        :param request:
        :return:
        """
        processed_query = {}
        for key, value in request.GET.items():
            processed_query[key] = value
        ali_sign = processed_query.pop('sign', None)

        alipay = AliPay(
            appid=APP_ID,
            app_notify_url=APP_NOTIFY_URL,
            app_private_key_path=PRIVATE_KEY_PATH,
            alipay_public_key_path=ALIPAY_KEY_PATH,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url=RETURN_URL
        )

        verify_re = alipay.verify(processed_query, ali_sign)

        if verify_re is True:
            order_sn = processed_query.get('out_trade_no', None)
            trade_no = processed_query.get('trade_no', None)
            trade_status = processed_query.get('trade_status', None)

            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                existed_order.trade_no = trade_no
                existed_order.trade_status = trade_status
                existed_order.pay_time = datetime.now()
                existed_order.save()

            response = redirect('index')
            response.set_cookie('nextPath', 'pay', max_age=3)
            return response
        else:
            response = redirect('index')
            return response

    def post(self, request):
        """
        处理支付宝的app_notify_url
        :param request:
        :return:
        """
        processed_query = {}
        for key,value in request.POST.items():
            processed_query[key] = value
        ali_sign = processed_query.pop('sign', None)

        alipay = AliPay(
            appid=APP_ID,
            app_notify_url=APP_NOTIFY_URL,
            app_private_key_path=PRIVATE_KEY_PATH,
            alipay_public_key_path=ALIPAY_KEY_PATH,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url=RETURN_URL
        )

        verify_re = alipay.verify(processed_query, ali_sign)

        if verify_re is True:
            order_sn = processed_query.get('out_trade_no', None)
            trade_no = processed_query.get('trade_no', None)
            trade_status = processed_query.get('trade_status', None)

            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                #修改商品的销售量。
                order_goods = existed_order.goods.all()
                for order_good in order_goods:
                    goods = order_good.goods
                    goods.sold_num += order_good.goods_num
                    goods.save()

                existed_order.trade_no = trade_no
                existed_order.trade_status = trade_status
                existed_order.pay_time = datetime.now()
                existed_order.save()

            return Response('success')