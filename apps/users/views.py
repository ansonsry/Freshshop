from django.shortcuts import render

# Create your views here.
from django.db.models import Q
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework.authentication import SessionAuthentication

from .serializers import SmsSerialiser, UserRegSerialiser, UserDetailSerialiser
from utils.YunPian import YunPian
from FreshShop.settings import APIKEY
from .models import VerifyCode

from random import choice

User = get_user_model()


class CustomBackend(ModelBackend):
        # 重写authenticate验证方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SmsSerialiser

    #生成随机验证码
    def generate_code(self):
        random_code = '1234567890'
        random_str = []
        for i in range(4):
            random_str.append(choice(random_code))
        return ''.join(random_str)

    #重写Create方法
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data['mobile']
        code = self.generate_code()
        yuan_pian = YunPian(APIKEY)
        sms_status = yuan_pian.send_sms(mobile=mobile, code=code)

        if sms_status['code'] != 0:
            return Response({
                'mobile': sms_status['msg']
            }, status.HTTP_400_BAD_REQUEST)
        else:
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()

            return Response({
                'mobile': mobile
            }, status.HTTP_201_CREATED)


class UserViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    #serializer_class = UserRegSerialiser
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    #动态设置serializer获取用户信息
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerialiser

        elif self.action == 'create':
            return UserRegSerialiser

        return UserDetailSerialiser


    #动态设置permissions获取用户信息
    def get_permissions(self):
        if self.action == 'retrieve' or 'partial_update' or 'update':
            return [permission() for permission in self.permission_classes]

        elif self.action == 'create':
            return []

        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()
