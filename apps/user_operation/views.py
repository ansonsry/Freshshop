from django.shortcuts import render

# Create your views here.
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import UserFavSerializers, UserFavDetailSerializers, UserLeavMessageSerializers,UserAddressSerializers
from utils.permissions import IsOwnerOrReadOnly

from .models import UserFav, UserLeavingMessage, UserAddress


class UserFavViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,\
                     viewsets.GenericViewSet):
    """
    list:
        收藏列表
    create:
        添加收藏
    destroy:
        取消收藏
    retrieve:
        判断某个商品是否收藏
    """
    # queryset = UserFav.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    serializer_class = UserFavSerializers
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = 'goods_id'

    def perform_create(self, serializer):
        """
        用户收藏的商品数量增加
        :param serializer:
        :return:
        """
        instance = serializer.save()
        goods = instance.goods
        goods.fav_num += 1
        goods.save()

    def perform_destroy(self, instance):
        """
        用户收藏商品的数量减少
        :param instance:
        :return:
        """
        goods = instance.goods
        goods.fav_num -= 1
        goods.save()
        instance.delete()

    def get_serializer_class(self):
        """
        动态的收藏信息
        :return:
        """
        if self.action == 'list':
            return UserFavDetailSerializers

        elif self.action == 'create':
            return UserFavSerializers

        return UserFavSerializers

    def get_queryset(self):
        return UserFav.objects.filter(user=self.request.user)


class UserLeavMessageViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin, \
                             viewsets.GenericViewSet):
    """
    list:
        留言列表
    create:
        添加留言
    destroy:
        删除留言
    """
    serializer_class = UserLeavMessageSerializers
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)


class UserAddressViewSet(viewsets.ModelViewSet):
    """
    list:
        收货地址列表
    create:
        添加新的收货地址
    update:
        修改收货地址
    delete:
        删除收货地址
    """
    serializer_class = UserAddressSerializers
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)
