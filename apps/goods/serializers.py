# _*_ coding: utf-8 _*_

# _Author_: 'Anson'

# _Time_: '2019-01-27 6:37'

from django.db.models import Q
from rest_framework import serializers
from goods.models import Goods, GoodsCategory, GoodsImage, Banner, GoodsCategoryBrand, IndexAd


# class GoodsSerializers(serializers.Serializer):
#     name = serializers.CharField(required=True, max_length=100)
#     click_num = serializers.IntegerField(default=0)
class CategorySerializers3(serializers.ModelSerializer):
    class Meta:
        model=GoodsCategory
        fields = "__all__"


class CategorySerializers2(serializers.ModelSerializer):
    sub_cat = CategorySerializers3(many=True)
    class Meta:
        model=GoodsCategory
        fields = "__all__"


class CategorySerializers(serializers.ModelSerializer):
    sub_cat = CategorySerializers2(many=True)
    class Meta:
        model=GoodsCategory
        fields = "__all__"


class GoodsImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ['image', ]


class GoodsSerializers(serializers.ModelSerializer):
    category = CategorySerializers()
    images = GoodsImageSerializers(many=True)
    class Meta:
        model = Goods
        # fields = ('name', 'click_num', 'market_price', 'add_time')
        fields = "__all__"


class BannerSerializers(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


class CategoryBrandSerializers(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


class IndexCategorySerializers(serializers.ModelSerializer):
    brands = CategoryBrandSerializers(many=True)
    goods = serializers.SerializerMethodField()
    sub_cat = CategorySerializers2(many=True)
    ad_goods = serializers.SerializerMethodField()

    def get_ad_goods(self, obj):
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id)
        if ad_goods:
            goods_ins = ad_goods[0].goods
            goods_json = GoodsSerializers(goods_ins, many=False, context={'request': self.context['request']}).data

        return goods_json

    def get_goods(self, obj):
        all_goods = Goods.objects.filter(Q(category_id=obj.id) | Q(category__parent_category_id=obj.id) | \
                               Q(category__parent_category__parent_category_id=obj.id))

        goods_serializer = GoodsSerializers(all_goods, many=True, context={'request': self.context['request']})

        return goods_serializer.data

    class Meta:
        model = GoodsCategory
        fields = "__all__"

