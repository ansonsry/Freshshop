# _*_ coding: utf-8 _*_

# _Author_: 'Anson'

# _Time_: '2019-05-13 15:41'

import requests
import json


class YunPian(object):
    def __init__(self,apikey):
        self.apikey = apikey
        self.single_send_url = 'https://sms.yunpian.com/v2/sms/single_send.json'

    def send_sms(self, mobile, code):
        parmas = {
            'apikey': self.apikey,
            'mobile': mobile,
            'text': '【赵安松】您的验证码是{code}。如非本人操作，请忽略本短信'.format(code=code)
        }
        response = requests.post(self.single_send_url, data=parmas)
        re_dict = json.loads(response.text)
        return re_dict


if __name__ == '__main__':
    yunpian = YunPian('')
    yunpian.send_sms('','2019')