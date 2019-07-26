"""FreshShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import xadmin
from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import path, include, re_path
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from FreshShop.settings import MEDIA_ROOT
from goods.views import CategoryListViewSet, GoodsListViewSet, GoodsListView, BannerViewSet, IndexCategoryViewSet
from users.views import SmsCodeViewSet, UserViewSet
from user_operation.views import UserFavViewSet, UserLeavMessageViewSet, UserAddressViewSet
from trade.views import ShoppingCartViewSet, OrderInfoViewSet, AliPayView

router = DefaultRouter()


#配置Category的URL
router.register('categorys', CategoryListViewSet, base_name='categorys')
#配置发送短信的URL
router.register('codes', SmsCodeViewSet, base_name='codes')
#配置Goods的URL
router.register('goods', GoodsListViewSet, base_name='goods')
#配置UserRegiste的URL
router.register('users', UserViewSet, base_name='users')
#用户收藏
router.register(r'userfavs', UserFavViewSet, base_name='userfavs')
#用户留言
router.register(r'userleavmessage', UserLeavMessageViewSet, base_name='userleavmessage')
#用户收货地址
router.register(r'address', UserAddressViewSet, base_name='address')
#购物车
router.register(r'shopcarts', ShoppingCartViewSet, base_name='shopcarts')
#订单
router.register(r'orders', OrderInfoViewSet, base_name='orders')
#轮播图
router.register(r'banners', BannerViewSet, base_name='banners')
#首页商品分类信息
router.register(r'indexgoods', IndexCategoryViewSet, base_name='indexgoods')
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('index',TemplateView.as_view(template_name='index.html'), name='index'),
    path('xadmin/', xadmin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # 配置上传文件的访问处理函数
    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    path('goodse/', GoodsListView.as_view(), name='goods-list'),
    path('docs/', include_docs_urls(title='freshshop')),
    path('', include(router.urls)),
    #JWT的Token认证
    path('login/', obtain_jwt_token),
    path('alipay/return', AliPayView.as_view(), name='alipay')
]
