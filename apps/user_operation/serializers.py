# _*_ coding: utf-8 _*_

# _Author_: 'Anson'

# _Time_: '2019-06-06 12:15'

from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers
from goods.serializers import GoodsSerializers
from .models import UserFav, UserLeavingMessage, UserAddress


class UserFavDetailSerializers(serializers.ModelSerializer):
    goods = GoodsSerializers()
    class Meta:
        model = UserFav
        fields = ('goods', 'id')


class UserFavSerializers(serializers.ModelSerializer):
    """获取当前用户"""
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message='该商品已收藏！',
            )
        ]
        model = UserFav
        fields = ('user', 'goods', 'id')


class UserLeavMessageSerializers(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserLeavingMessage
        fields = ('message_type', 'user', 'message', 'subject', 'file', 'add_time', 'id')


class UserAddressSerializers(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserAddress
        fields = ('user', 'province', 'city', 'district', 'address', 'signer_name', 'signer_mobile', 'id')