# -*- coding: utf-8 -*-
"""
cron: 0 0 */4 * * ?
new Env('太太乐餐饮');
本脚本支持新版青龙环境变量，变量名：ttlhd，支持青龙推送消息
微信搜索太太乐餐饮注册登录，下载太太乐app兑换话费及其他实物
首次注册必须先登录一次小程序绑定微信然后再获取token不会抓包的小白使用api接口获取token
https://www.ttljf.com/ttl_site/user.do?username=手机号码&password=密码&device_brand=apple&device_model=iPhone11,8&device_uuid=&device_version=13.5&mthd=login&platform=ios&sign="
复制链接浏览器打开，换成自己账户密码，
"""
import os
import sys
import json
import re
import time

import requests
from sendNotify import send

def load_send():
    global send
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/sendNotify.py"):
        try:
            from sendNotify import send
        except:
            send=False
            printf("加载通知服务失败~")
    else:
        send=False
        printf("加载通知服务失败~")
load_send()

def get_token():
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
        if json.loads(response.text)['data'][i]['name'] =='ttlhd':
            try:
                token = json.loads(response.text)['data'][i]['value'].split('&')
                tokens.extend(token)
            except:
                pass
    return tokens


class Ttl:
    def __init__(self,tokens):
        self.tokens = tokens

    def task(self,token):
        url = 'https://www.ttljf.com/ttl_chefHub/'
        headers ={
            'Host': 'www.ttljf.com',
            'Accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'token': token,
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Encoding': 'gzip,compress,br,deflate',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.14(0x18000e2f) NetType/4G Language/zh_CN',
            'Referer': 'https://servicewechat.com/wxe9aa8f1c4a77ddf5/17/page-frame.html',
             }
        #分享任务
        response = requests.put(url+
            'Common/share/A35D575F-C004-4717-AABC-ED9D1979C3FA/blog', headers=headers)
        data = json.loads(response.text)
        if data['code'] == 0:
            print(f"分享任务：{data['message']},获得1积分")
        else:
            print(f"分享任务：{data['message']}")
        #签到任务
        result = requests.put(url+'user/api/sign/today', headers=headers)
        res = json.loads(result.text)
        if res['code'] == 0:
            print(f"签到任务：{res['message']},获得1积分")
        else:
            print(f"签到任务：{res['message']}")

    def info(self,token):
        msg = []
        url = 'https://www.ttljf.com/ttl_chefHub/'
        headers ={
            'Host': 'www.ttljf.com',
            'Accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'token': token,
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Encoding': 'gzip,compress,br,deflate',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.14(0x18000e2f) NetType/4G Language/zh_CN',
            'Referer': 'https://servicewechat.com/wxe9aa8f1c4a77ddf5/17/page-frame.html', 
            }
            #积分余额
        response = requests.get(url+'user/api/my', headers=headers)
        res = json.loads(response.text)
        total = res.get('data')
        if res['code'] == 0:
            print(f"账户当前积分：{total['integral']}")
            msg.append(f"积分：{total['integral']}")
        else:
            print("token失效,请重新获取")
            msg.append(":token失效")
        return msg

    #商品库存
    def repertory(self):
        msg = []
        url = 'https://www.ttljf.com/ttl_site/giftApi.do?giftCategoryId=7&mthd=searchGift&pageNo=1&pageSize=10&sign=ba06bb1cc4ec3e6518e29ca17599b356'
        headers = {
            'Host': 'www.ttljf.com',
            'Accept': '*/*',
            'Cookie': 'agreePrivacy=false; JSESSIONID=1B106F78B0E7D4A7E997E27E778E90BA',
            'User-Agent': 'Totole/1.4.8 (iPhone; iOS 15.3; Scale/3.00)',
            'Accept-Language': 'zh-Hans-CN;q=1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
            }
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        giftlist = data.get('gifts')
        for item in giftlist:
            print("=============📣系统通知📣=============")
            print(item["giftName"]+ "  库存为："+str(item["giftCount"])+ "  所需积分："+str(item["price"]))
            msg.append(item["giftName"]+ "  库存为："+str(item["giftCount"])+ "  所需积分："+str(item["price"]))
        return msg

    def main(self,tokens):
        msg = []
        msg_0 = []
        i = 1
        announce = "🔔太太乐任务开始\n第一次注册必须先登录一次小程序绑定微信然后再获取token\n"
        announce += "不会抓包的小白使用api接口获取token,脚本支持新版青龙环境变量，变量名：ttlhd\n"
        announce += "有问题请看脚本注释\n\n\n" 
        print(announce)
        msg_1 = self.repertory()
        for token in tokens:
            try:
                print("-----------------------------------------")
                print(f"\n执行第{i}个账号任务")
                self.task(token)
                a = self.info(token)
                msg_0.append(f"第{i}个账号"+ a[0])
                i += 1
            except:
                print("请检查token前后是否有空格")
                i += 1
        print("\n任务执行完毕！")
        msg = msg_0 + msg_1
        return msg


if __name__ == '__main__':
    msg = ''
    tokens = get_token()
    ttl = Ttl(tokens)
    msgs = ttl.main(tokens)
    for m in msgs:
        msg += "\n"+m
    msg += "\n"+"时间："+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    send("太太乐通知",msg)


