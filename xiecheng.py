# -*- coding: utf-8 -*-
"""
cron: 5 11,19 * * *
new Env('携程签到');
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


#获取变量token
def get_token_userid():
    tokens = []
    url='http://127.0.0.1:5600/api/envs'
    with open('/ql/config/auth.json', 'r') as f:
        token=json.loads(f.read())['token']
    headers={
        'Accept':'application/json',
        'authorization':'Bearer '+token,
        }
    response=requests.get(url=url,headers=headers)
    for i in range(len(json.loads(response.text)['data'])):
        if json.loads(response.text)['data'][i]['name'] =='xiecheng':
            try:
                env = re.split("&|,|，|\\s",json.loads(response.text)['data'][i]['value'])
                for item in env:
                    if item == '':
                        pass
                    else:
                        tokens.append(item)
            except:
                pass
    return tokens

def send_request(token):
    url = 'https://m.ctrip.com/restapi/soa2/22769/signToday?_fxpcqlniredt=12001026110277350067&x-traceID=12001026110277350067-1720117535098-7995090'

    headers = {
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'Origin': 'https://m.ctrip.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20D67_eb64__isiPhoneX_Ctrip_CtripWireless_8.71.2_cDevice=iPhone 14 Pro__cSize=w393*h852__cwk=1_safeAreaTop=59_safeAreaBottom=34',
        'Cookie': '_MKT_code=PUSHCODE=mypoint&createtime=1720117339',
        'Host': 'm.ctrip.com',
        'Referer': 'https://m.ctrip.com/activitysetupapp/mkt/index/membersignin2021?isHideNavBar=YES&pushcode=mypoint&from_native_page=1&fromMemberTab=point',
        'cookieOrigin': 'https://m.ctrip.com',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Accept': '*/*'
    }

    body = {
        "platform": "APP",
        "openId": "",
        "rmsToken": "",
        "head": {
            "cid": "12001026110277350067",
            "ctok": "",
            "cver": "871.002",
            "lang": "01",
            "sid": "8890",
            "syscode": "12",
            "auth": token,
            "xsid": "",
            "extension": []
        }
    }

    response = requests.post(url, json=body, headers=headers)
    res = response.json()
    msg = f"携程签到结果：{res['message']}"
    return msg




tokens = get_token_userid()
msg = ''
for token in tokens:
    msg += send_request(token)
send("携程签到通知",msg)
