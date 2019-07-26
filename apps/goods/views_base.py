# _*_ coding: utf-8 _*_

# _Author_: 'Anson'

# _Time_: '2019-01-27 4:58'

from django.views.generic import View
from .models import Goods


class GoodsListViews(View):
    def get(self,request):
        goods_list = []
        goods = Goods.objects.all()[:10]
        # for good in goods:
        #     json_dict = {}
        #     json_dict['name'] = good.name
        #     json_dict['category'] = good.category.name
        #     json_dict['market_price'] = good.market_price
        #     print(json_dict)
        #     goods_list.append(json_dict)

        # model_to_dict 的使用

        # from django.forms.models import model_to_dict
        # for good in goods:
        #     json_dict = model_to_dict(good)
        #     goods_list.append(json_dict)
        import json
        from django.core import serializers
        json_data = serializers.serialize('json', goods)
        json_data = json.loads(json_data)

        from django.http import HttpResponse, JsonResponse


        #return HttpResponse(json_data, content_type='application/json')
        return JsonResponse(json_data, safe=False)