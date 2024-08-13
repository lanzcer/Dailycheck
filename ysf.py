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
        self.base_url = 'https://upa.jieyou.pro:9192/yhjx/api/draw/turntable'
        self.headers = {
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'saleWay': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://mini.jieyou.pro',
            'User-Agent': ('Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 '
                           '(KHTML, like Gecko) Mobile/15E148 /sa-sdk-ios/sensors-verify/analytics.95516.com?production '
                           '(com.unionpay.chsp) (cordova 4.5.4) (updebug 0) (version 1010) (UnionPay/1.0 CloudPay) '
                           '(clientVersion 310) (language zh_CN) (languageFamily zh_CN) (upApplet single) (walletMode 00)'),
            'Host': 'upa.jieyou.pro:9192',
            'Referer': 'https://mini.jieyou.pro/',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Accept': '*/*'
        }

    def send_post_request(self, endpoint, body):
        url = f'{self.base_url}/{endpoint}'
        try:
            response = requests.post(url, headers=self.headers, data=body)
            response.raise_for_status()
            return response.json()  # 返回JSON响应内容
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")
        return None

    def sign(self):
        endpoint = 'signV3'
        body = 'channelId=1&type=1'
        sign_res = self.send_post_request(endpoint, body)
        if sign_res and sign_res.get('code') == 200:
            return "签到成功，获得一次抽奖机会"
        else:
            return sign_res.get('msg', '签到失败')

    def draw(self):
        endpoint = 'doDrawV1'
        body = 'type=1'
        draw_res = self.send_post_request(endpoint, body)
        if draw_res and draw_res.get('code') == 200:
            return f"{draw_res['msg']}, 获得奖品: {draw_res['data']['name']}"
        else:
            return draw_res.get('msg', '抽奖失败')

    def refresh(self):
        url = "https://upa.jieyou.pro:9192/yhjx/api/mini/addUserLoginRecord"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            res = response.json().get('msg', '刷新失败')
            print(res)
            return res
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")
        return None

    def main(self):
        msg = ''
        for i, token in enumerate(self.tokens, start=1):
            self.headers['Authorization'] = f'Bearer {token}'
            self.refresh()
            msg += f"【执行第{i}个账号任务】\n"
            msg += self.sign() + ', '
            msg += self.draw() + '\n'
        print(msg)
        return msg

if __name__ == '__main__':
    tokens = get_token_userid()
    ysf = YSFSIGN(tokens)
    msg = ysf.main()
    msg += f"\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    send("云闪付签到通知", msg)
