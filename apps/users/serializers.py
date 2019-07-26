# _*_ coding: utf-8 _*_

# _Author_: 'Anson'

# _Time_: '2019-05-13 16:07'

from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.contrib.auth import get_user_model
from FreshShop.settings import REGEX_MOBILE
from datetime import timedelta, datetime
from .models import VerifyCode
import re

User = get_user_model()


class SmsSerialiser(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):
        #验证手机是否注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError('该手机号已经存在！')
        #验证手机号码是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError('手机号码格式不正确！')
        #验证短信发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago,mobile=mobile).count():
            raise serializers.ValidationError('距离上次一发送短信未超过60s！')

        return mobile


class UserDetailSerialiser(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'birthday', 'gender', 'email', 'mobile')


class UserRegSerialiser(serializers.ModelSerializer):
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label='验证码', error_messages={
        'blank': '请输入验证码！',
        'max_length': '验证码格式错误！',
        'min_length': '验证码格式错误！',
        'required': '验证码不能为空！',
    }, help_text='验证码')
    username = serializers.CharField(required=True, allow_blank=False,\
                                     validators=[UniqueValidator(queryset=User.objects.all(), message='用户名已经存在！')])

    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    # def create(self, validated_data):
    #     user = super(UserRegSerialiser, self).create(validated_data = validated_data)
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user

    def validate_code(self, code):
        print('进来了！')
        Verify_records = VerifyCode.objects.filter(mobile=self.initial_data['username']).order_by('-add_time')
        if Verify_records:
            last_records = Verify_records[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_records.add_time:
                raise serializers.ValidationError('验证码已经过期')

            if last_records.code != code:
                raise serializers.ValidationError('验证码错误！')

        else:
            raise serializers.ValidationError('验证码错误！')

    def validate(self, attrs):
        attrs['mobile'] = attrs['username']
        del attrs['code']
        return attrs

    class Meta:
        model = User
        fields = ('username', 'mobile', 'code', 'password')
