from django.shortcuts import render

# Create your views here.
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, viewsets, mixins, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend

from .models import Goods, GoodsCategory, Banner, GoodsCategoryBrand
from .serializers import GoodsSerializers, CategorySerializers, BannerSerializers, IndexCategorySerializers
from .filters import GoodsFilter


# class GoodsListView(APIView):
#     '''
#     List all goods
#     '''
#     def get(self, request, format=None):
#         goods = Goods.objects.all()[:10]
#         goodSerializer = GoodsSerializers(goods, many=True)
#         return Response(goodSerializer.data)


# class GoodsListView(mixins.ListModelMixin, generics.ListAPIView):
#     queryset = Goods.objects.all()[:10]
#     serializer_class = GoodsSerializers
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

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


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 1000


class GoodsListView(generics.ListAPIView):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializers
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name', 'market_price')
    ordering_fields = ('sold_num', 'shop_price')


class GoodsListViewSet(CacheResponseMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    商品的列表，过滤，分页，详情
    """
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializers
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = GoodsFilter
    search_fields = ('name', 'goods_brief', 'goods_desc')
    ordering_fields = ('sold_num', 'shop_price')

    def retrieve(self, request, *args, **kwargs):
        """
        商品点击数
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    '''
    list:
        商品类别信息
    '''
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializers


class BannerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Banner.objects.all().order_by('index')
    serializer_class = BannerSerializers


class IndexCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = GoodsCategory.objects.filter(is_tab=True)
    serializer_class = IndexCategorySerializers