# -*- coding: utf-8 -*-
"""
cron: 0 0/30 * * * ?
new Env('太太乐话费库存监控、兑换');，
不成熟脚本，有待测试
本脚本支持新版青龙环境变量ttlhd，支持青龙推送消息
如需自动兑换话费，需要token和userId
填写方式如:aaaa-bbbb-cccc-dddd-eeee,111111
多账号用&连接或者另加同名变量
接口:https://www.ttljf.com/ttl_site/user.do?username=账号&password=密码&device_brand=apple&device_model=iPhone11,8&device_uuid=&device_version=13.5&mthd=login&platform=ios&sign=
如脚本报{"killed":false,"code":1,"signal":null,"cmd":"kill -9 3","stdout":"","stderr":"sh: can't kill pid 3: No such process"}
修改服务器/etc/systemd/logind.conf文件，将KillUserProcesses=no前面的//删除
"""
import os
import sys
import json
import re
import time

import requests
from sendNotify import send

#加载通知服务
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


#获取变量token，userid
def get_token_userid():
    tokens = []
    users = []
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
                env = re.split("&|,|，|\\s",json.loads(response.text)['data'][i]['value'])
                for item in env:
                    if item == '':
                        pass
                    elif len(item) <=8:
                        users.append(item)
                    else:
                        tokens.append(item)
            except:
                pass
    return tokens, users


def giftInven():
    flag = False
    k = 0
    url = 'https://www.ttljf.com/ttl_site/giftApi.do?giftCategoryId=7&mthd=searchGift&pageNo=1&pageSize=10&sign='
    headers = {
        'Host': 'www.ttljf.com',
        'Accept': '*/*',
        'User-Agent': 'Totole/1.4.8 (iPhone; iOS 15.3; Scale/3.00)',
        'Accept-Language': 'zh-Hans-CN;q=1',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
        }
    while flag == False:
        if k < 150:
            response = requests.get(url, headers=headers)
            for i in range(len(json.loads(response.text)['gifts'])):
                if json.loads(response.text)['gifts'][i]['stockAmount'] != 0:
                    giftname = json.loads(response.text)['gifts'][i]['giftName']
                    stockamount = json.loads(response.text)['gifts'][i]['stockAmount']
                    return 1
                elif json.loads(response.text)['gifts'][i]['stockAmount'] == 0:
                    giftname = json.loads(response.text)['gifts'][i]['giftName']
                    print(f"{giftname}暂时无货")
            print("等待10s继续查看库存")
            time.sleep(10)
            k += 1     
        else:
            flag = True

def stock():
    msg = ''
    url = 'https://www.ttljf.com/ttl_site/giftApi.do?giftCategoryId=7&mthd=searchGift&pageNo=1&pageSize=10&sign='
    headers = {
        'Host': 'www.ttljf.com',
        'Accept': '*/*',
        'User-Agent': 'Totole/1.4.8 (iPhone; iOS 15.3; Scale/3.00)',
        'Accept-Language': 'zh-Hans-CN;q=1',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
        }
    response = requests.get(url, headers=headers)
    for i in range(len(json.loads(response.text)['gifts'])):
        giftname = json.loads(response.text)['gifts'][i]['giftName']
        stockamount = json.loads(response.text)['gifts'][i]['stockAmount']
        msg += giftname+'剩余库存：'+str(stockamount)+'\n'
    return msg


class Buygift:
    def __init__(self,signal):
        self.signal = signal
    #获取token对应手机号码
    def get_phone(self,token):
        nums = []
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
        response = requests.get(url+'user/api/my', headers=headers)
        if json.loads(response.text)['code'] == 0:
            nums.append(json.loads(response.text)['data']['mobile'])
        else:
            nums.append('')

    #识别手机号码运营商
    def identify_num(self,phone_number):
        China_Tele = ['133','149','153','173','177','180','181','189','199']
        China_Unic = ['130','131','132','145','155','156','166','171','175','176','185','186']
        China_Mobi = ['134','135','136','137','138','139','147','150','151','152','157','158','159','178','182','183','184','187','188','198']
        if phone_number[0:3] in China_Tele:
            return 1
        elif phone_number[0:3] in China_Unic:
            return 2
        elif phone_number[0:3] in China_Mobi:
            return 3

    def gift61(self,token,user):
        url= 'https://www.ttljf.com/ttl_site/giftApi.do?gifts=61%3A1&loginToken=&mthd=buyGift&sign=&totalprice=3&userId='
        url = list(url+user)
        url.insert(66, token)
        url = ''.join(url)
        headers ={
            'Host': 'www.ttljf.com',
            'Accept': '*/*',
            'User-Agent': 'Totole/1.4.8 (iPhone; iOS 15.3; Scale/3.00)',
            'Accept-Language': 'zh-Hans-CN;q=1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers)
        return json.loads(response.text)['code'], json.loads(response.text)['message']

    def gift62(self,token,user):
        url= 'https://www.ttljf.com/ttl_site/giftApi.do?gifts=62%3A1&loginToken=&mthd=buyGift&sign=&totalprice=7&userId='
        url = list(url+user)
        url.insert(66, token)
        url = ''.join(url)
        headers ={
            'Host': 'www.ttljf.com',
            'Accept': '*/*',
            'User-Agent': 'Totole/1.4.8 (iPhone; iOS 15.3; Scale/3.00)',
            'Accept-Language': 'zh-Hans-CN;q=1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers)
        return json.loads(response.text)['code'], json.loads(response.text)['message']

    def gift633(self,token,user):
        url= 'https://www.ttljf.com/ttl_site/giftApi.do?gifts=633%3A1&loginToken=&mthd=buyGift&sign=&totalprice=45&userId='
        url = list(url+user)
        url.insert(67, token)
        url = ''.join(url)
        headers ={
            'Host': 'www.ttljf.com',
            'Accept': '*/*',
            'User-Agent': 'Totole/1.4.8 (iPhone; iOS 15.3; Scale/3.00)',
            'Accept-Language': 'zh-Hans-CN;q=1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers)
        return json.loads(response.text)['code'], json.loads(response.text)['message']


    def gift631(self,token,user):
        url= 'https://www.ttljf.com/ttl_site/giftApi.do?gifts=631%3A1&loginToken=&mthd=buyGift&sign=&totalprice=15&userId='
        url = list(url+user)
        url.insert(67, token)
        url = ''.join(url)
        headers ={
            'Host': 'www.ttljf.com',
            'Accept': '*/*',
            'User-Agent': 'Totole/1.4.8 (iPhone; iOS 15.3; Scale/3.00)',
            'Accept-Language': 'zh-Hans-CN;q=1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers)
        return json.loads(response.text)['code'], json.loads(response.text)['message']

    def main(self):
        nums = []
        msg_all = []
        tokens = get_token_userid()[0]
        users = get_token_userid()[1]
        for token in tokens:
            nums.append(self.get_phone())
        for i in range(len(tokens)):
            if nums[i] == '':
                print(f"账号{i}token失效")
                s = '账号'+str(i)+'token失效'
                msg_all += s
            elif self.identify_num(nums[i]) == 1:
                code = self.gift633(tokens[i],users[i])[0]
                msg = self.gift633(tokens[i],users[i])[1]
                if code == '0000':
                    print(f"{nums[i]}兑换5元话费成功")
                    a = "手机号："+nums[i]+",兑换15元话费成功"
                else:
                    print(f"{nums[i]}兑换5元话费失败")
                    a = "手机号："+nums[i]+",兑换15元话费失败\n原因："+msg
                msg_all.append(a)
            elif self.identify_num(nums[i]) == 2:
                code_1 = self.gift62(tokens[i],users[i])[0]
                msg_1 = self.gift62(tokens[i],users[i])[1]
                if code_1 == '0000':
                    print(f"{nums[i]}兑换5元话费成功")
                    b = "手机号："+nums[i]+",兑换5元话费成功"
                else:
                    print(f"{nums[i]}兑换5元话费失败")
                    b = "手机号："+nums[i]+",兑换5元话费失败\n原因："+msg_1
                msg_all.append(b)
                code_2 = self.gift61(tokens[i],users[i])[0]
                msg_2 = self.gift61(tokens[i],users[i])[1]                
                if code_1 == '0000':
                    print(f"{nums[i]}兑换2元话费成功")
                    c = "手机号："+nums[i]+",兑换2元话费成功"
                else:
                    print(f"{nums[i]}兑换2元话费失败")
                    c = "手机号："+nums[i]+",兑换2元话费失败\n原因："+msg_2
                msg_all.append(c)
            elif self.identify_num(nums[i]) == 3:
                code_3 = self.gift631(tokens[i],users[i])[0]
                msg_3 = self.gift631(tokens[i],users[i])[1]                  
                if code_3 == '0000':
                    print(f"{nums[i]}兑换30元话费成功")
                    d = "手机号："+nums[i]+",兑换30元话费成功"
                else:
                    print(f"{nums[i]}兑换5元话费失败")
                    d = "手机号："+nums[i]+",兑换5元话费失败\n原因："+msg_3
                msg_all.append(d)
        print("自动兑换结束，请登录太太乐app查看")
        return msg_all


if __name__ == '__main__':
    print("必须变量token,userId,在接口处都可获得，填写方式见脚本注释")
    print("----------太太乐话费库存监控开始----------")
    signal = giftInven()
    if signal == 1:
        msg = stock()
        send("太太乐库存通知",msg)
        buygift = Buygift(signal)
        message = buygift.main()
        send("太太乐话费兑换通知",message)


