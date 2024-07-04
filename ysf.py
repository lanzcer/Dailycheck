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

# 通知服务配置
BARK = os.getenv("BARK", '')  # bark服务,自行搜索; secrets可填;
BARK_PUSH = os.getenv("BARK_PUSH", '')  # bark自建服务器，要填完整链接，结尾的/不要
QYWX_AM = os.getenv("QYWX_AM", '')  # 企业微信
QYWX_KEY = os.getenv("QYWX_KEY", '')

notify_mode = []
message_info = ''

if BARK or BARK_PUSH:
    notify_mode.append('bark')
if QYWX_AM:
    notify_mode.append('wecom_app')

def message(str_msg):
    global message_info
    print(str_msg)
    message_info = f"{message_info}\n{str_msg}"
    sys.stdout.flush()

def bark(title, content):
    print("\n")
    if BARK:
        try:
            response = requests.get(f"https://api.day.app/{BARK}/{title}/{urllib.parse.quote_plus(content)}").json()
            if response['code'] == 200:
                print('推送成功！')
            else:
                print('推送失败！')
        except Exception as e:
            print(f'推送失败！错误: {e}')
    if BARK_PUSH:
        try:
            response = requests.get(f"{BARK_PUSH}/{title}/{urllib.parse.quote_plus(content)}").json()
            if response['code'] == 200:
                print('推送成功！')
            else:
                print('推送失败！')
        except Exception as e:
            print(f'推送失败！错误: {e}')
    if not BARK and not BARK_PUSH:
        print("bark服务的bark_token未设置!!\n取消推送")

def wecom_key(title, content):
    print("\n")
    if not QYWX_KEY:
        print("QYWX_KEY未设置!!\n取消推送")
        return
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": title + "\n" + content.replace("\n", "\n\n")
        }
    }
    response = requests.post(f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={QYWX_KEY}", json=data, headers=headers).json()
    print(response)

def wecom_app(title, content):
    try:
        if not QYWX_AM:
            print("QYWX_AM 并未设置！！\n取消推送")
            return
        QYWX_AM_AY = QYWX_AM.split(',')
        if len(QYWX_AM_AY) < 4:
            print("QYWX_AM 设置错误！！\n取消推送")
            return
        corpid, corpsecret, touser, agentid = QYWX_AM_AY[:4]
        media_id = QYWX_AM_AY[4] if len(QYWX_AM_AY) > 4 else ''
        wx = WeCom(corpid, corpsecret, agentid)
        message = f"{title}\n\n{content}"
        if not media_id:
            response = wx.send_text(message, touser)
        else:
            response = wx.send_mpnews(title, content, media_id, touser)
        if response == 'ok':
            print('推送成功！')
        else:
            print(f'推送失败！错误信息如下：\n{response}')
    except Exception as e:
        print(e)

class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid

    def get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': self.CORPID, 'corpsecret': self.CORPSECRET}
        req = requests.post(url, params=values)
        data = req.json()
        return data["access_token"]

    def send_text(self, message, touser="@all"):
        send_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.get_access_token()}'
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {"content": message},
            "safe": "0"
        }
        respone = requests.post(send_url, json=send_values).json()
        return respone["errmsg"]

    def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.get_access_token()}'
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [{
                    "title": title,
                    "thumb_media_id": media_id,
                    "author": "Author",
                    "content_source_url": "",
                    "content": message.replace('\n', '<br/>'),
                    "digest": message
                }]
            }
        }
        respone = requests.post(send_url, json=send_values).json()
        return respone["errmsg"]

def send(title, content):
    """
    使用 bark, 企业微信应用消息发送手机推送
    :param title:
    :param content:
    :return:
    """
    for mode in notify_mode:
        if mode == 'bark':
            bark(title=title, content=content)
        elif mode == 'wecom_app':
            wecom_app(title=title, content=content)
        else:
            print(f'此类推送方式不存在: {mode}')

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

    def send_post_request(self, endpoint, body,token):
        url = f'{self.base_url}/{endpoint}'
        headers = self.headers.copy()  # 复制通用头部
        headers['Authorization'] = f'Bearer {token}'  # 添加Authorization头

        try:
            response = requests.post(url, headers=headers, data=body)
            response.raise_for_status()
            return response.json()  # 返回JSON响应内容
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")
        return None

    def sign(self,token):
        endpoint = 'sign'
        body = 'channelId=1&type=1'
        sign_res =  self.send_post_request(endpoint, body,token)
        if sign_res['code'] == 200:
            a = f"签到成功，获得一次抽奖机会"
        else:
            a = sign_res['msg']
        return a


    def draw(self,token):
        endpoint = 'doDrawV1'
        body = 'type=1'
        draw_res =  self.send_post_request(endpoint, body,token)
        if draw_res['code'] == 200:
            b = f"{draw_res['msg']},获得奖品:{draw_res['data']['name']}"
        else:
            b = f"{draw_res['msg']}"
        return b

    def main(self,tokens):
        msg = ''
        i=1
        for token in tokens:
            msg += f"【执行第{i}个账号任务】\n" + self.sign(token) + ','
            msg += self.draw(token) + '\n'
            i += 1
        print(msg)
        return msg

if __name__ == '__main__':
    tokens = get_token_userid()
    ysf = YSFSIGN(tokens)
    msg = ysf.main(tokens)
    msg += f"\n时间：{(datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}"
    send("云闪付签到通知", msg)
