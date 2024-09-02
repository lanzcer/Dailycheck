# -*- coding: utf-8 -*-
"""
cron: 0 0,12 * * *
new Env('云闪付签到抽奖');
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
        if json.loads(response.text)['data'][i]['name'] =='ysf':
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

class YSFSIGN:
    def __init__(self, tokens):
        self.tokens = tokens
        self.base_url = 'https://paas-up-uhq-api.inrice.cn/finme-activity-server/api/activity/'
        self.headers = {
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'appId': '1461820386848097',
            'Origin': 'https://paas-up-uhq.inrice.cn',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 /sa-sdk-ios/sensors-verify/analytics.95516.com?production             (com.unionpay.chsp) (cordova 4.5.4) (updebug 0) (version 1012) (UnionPay/1.0 CloudPay) (clientVersion 312) (language zh_CN) (languageFamily zh_CN) (upApplet single) (walletMode 00) ',
            'app': 'UHJX',
            'Host': 'paas-up-uhq-api.inrice.cn',
            'Referer': 'https://paas-up-uhq.inrice.cn/',
            'Act-Key': 'ACT20240831132725AK7W',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9'
        }

    def send_post_request(self, endpoint,actkey):
        self.headers["Act-Key"] = actkey
        url = f'{self.base_url}/{endpoint}'
        response = requests.post(url, headers=self.headers)
        return response

    def sign(self):
        endpoint = 'sign-in'
        act_key = 'ACT20240831132725AK7W'
        sign_res = self.send_post_request(endpoint,act_key)
        if sign_res.status_code == 200:
            return "签到成功，获得一次抽奖机会"
        else:
            return sign_res.json().get('message', '签到失败')

    def draw(self):
        endpoint = 'lottery/participate'
        act_key = 'ACT20240831170440UJJ2'
        draw_res = self.send_post_request(endpoint,act_key)
        if draw_res.status_code == 200:
            return f"抽奖成功, 获得奖品: {draw_res.json()['prizeName']}"
        else:
            return draw_res.json().get('message')


    def main(self):
        msg = ''
        for i, token in enumerate(self.tokens, start=1):
            self.headers['Authorization'] = f'Bearer {token}'
            msg += f"【执行第{i}个账号任务】\n"
            msg += self.sign()
            msg += self.draw() + '\n'
        print(msg)
        return msg

if __name__ == '__main__':
    tokens = get_token_userid()
    ysf = YSFSIGN(tokens)
    msg = ysf.main()
    msg += f"\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    send("云闪付签到通知", msg)
