# -*- coding: utf-8 -*-
"""
cron: 6 12 * * *
new Env('工行刮刮乐');
"""

import sys
import os
import re
import requests
import json
import time
import urllib.parse
from requests.adapters import HTTPAdapter
from datetime import datetime, timedelta
from urllib3.util import Retry
from notify import send


def get_cookie():
    cookies = []
    url='http://127.0.0.1:5600/api/envs'
    with open('/ql/config/auth.json', 'r') as f:
        token=json.loads(f.read())['token']
    headers={
        'Accept':'application/json',
        'authorization':'Bearer '+token,
        }
    response=requests.get(url=url,headers=headers)
    for i in range(len(json.loads(response.text)['data'])):
        if json.loads(response.text)['data'][i]['name'] =='icbc':
            try:
                env = re.split("&",json.loads(response.text)['data'][i]['value'])
                for item in env:
                    if item == '':
                        pass
                    else:
                        cookies.append(item)
            except:
                pass
    return cookies


class ICBC:
    def __init__(self, cookie):
        self.cookie = cookie
        self.base_url = "https://chp.icbc.com.cn/bmcs/api-bmcs/lott/h5/lottery?corpId=2000000882"
        self.headers = {
            'method': 'POST',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://chp.icbc.com.cn',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 F-OFST  elife_moblie_ios  fullversion:6.1.2  BSComponentVersion:5.4 WorkStationChannel:0 isBreak:0  ICBCiPhoneBSNew 6.1.2 iphone os wkwebview:true',
            'Cookie': self.cookie,
            'Host': 'chp.icbc.com.cn',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Accept': 'application/json'
        }

    def send_request(self, act_id, referer):
        self.headers['Referer'] = referer
        body = json.dumps({"actId": act_id, "isApp": "1"})

        try:
            response = requests.post(self.base_url, headers=self.headers, data=body)
            response.raise_for_status()  # Raise an error for bad status codes
            response_data = response.json()
            if response_data['data']['returnCode'] == 0:
                goods_simple_name = response_data['data']['data']['goodsSimpleName']
            else:
                goods_simple_name = response_data['data']['returnMsg']
            return goods_simple_name
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def meishi(self):
        act_id = "LOT20241030084542687155"
        referer = "https://chp.icbc.com.cn/bmcs/lottery/?corpId=2000000882&actId=LOT20241030084542687155&isApp=1"
        return self.send_request(act_id, referer)

    def leyuan(self):
        act_id = "LOT20241031180517775971"
        referer = "https://chp.icbc.com.cn/bmcs/lottery/?corpId=2000000882&actId=LOT20241031093208130170&isApp=1"
        return self.send_request(act_id, referer)


    def movie(self):
        act_id = "LPARK20250122145738360581"
        referer = "https://chp.icbc.com.cn/bmcs/lottery/?corpId=2000000882&actId=LPARK20250122145738360581&isApp=1"
        return self.send_request(act_id, referer)

    def waimai(self):
        act_id = "LOT20250225142405675273"
        referer = "https://chp.icbc.com.cn/bmcs/lottery/?corpId=2000000882&actId=LOT20250225142405675273&isApp=1"
        return self.send_request(act_id, referer)

    def market(self):
        act_id = "LPARK20240628090153620720"
        referer = "https://chp.icbc.com.cn/bmcs/lottery/?corpId=2000000882&actId=LPARK20240628090153620720&isApp=1"
        return self.send_request(act_id, referer)

    def main(self):
        msg = ''
        print("******开始工行刮刮乐,间隔4s******")
        try:
            """self.meishi()
            time.sleep(2)
            meishi_msg = "【美食刮刮乐】" + self.meishi() + "\n"
            time.sleep(2)
            self.leyuan()
            time.sleep(2)
            leyuan_msg = "【乐园刮刮乐】" + self.leyuan() + "\n"
            time.sleep(2)
            self.movie()
            time.sleep(2)
            movie_msg = "【电影刮刮乐】" + self.movie() + "\n"
            time.sleep(2)"""
            self.waimai()
            time.sleep(2)
            waimai_msg = "【外卖刮刮乐】" + self.waimai() + "\n"
            #msg =meishi_msg + movie_msg + waimai_msg + leyuan_msg
            msg = waimai_msg
        except :
            msg += "token失效，请更新工行活动token"
        return msg

cks = get_cookie()
for ck in cks:
    icbc = ICBC(ck)
    msg = icbc.main()
    print(msg)
    send("【工行刮刮乐活动通知】",msg)








