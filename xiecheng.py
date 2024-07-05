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

# 通知服务配置
BARK = os.getenv("BARK", '')  # bark服务,自行搜索; secrets可填;
BARK_PUSH = os.getenv("BARK_PUSH", 'https://api.day.app/ra7fgu4whtBQKbqVxeb9Bj')  # bark自建服务器，要填完整链接，结尾的/不要
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
