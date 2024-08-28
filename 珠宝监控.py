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

LOCK_FLAG = True
ORDER_LIMIT = 3
# 通知服务
BARK = ''  # bark服务,自行搜索; secrets可填;
BARK_PUSH = ''  # bark自建服务器，要填完整链接，结尾的/不要
QYWX_AM = 'wwba9a8db44b3f1f11,SnL28v5S4JOOEErYiFrsEvs3EMcBxZCveRMCFnCUvpQ,@all,1000002,2-J9UzislOXozfzmdhPPrfRT5RtKNQnYU_MC8hoQsBeo'  # 企业微信
PUSH_PLUS_TOKEN = ''
PUSH_PLUS_USER = ''
WXPUSH_TOKEN = 'AT_maOBarRKI5ZBSTXg3e2pOatL5KMW4IbK'
WXPUSH_TOPIC = 32978
notify_mode = []
message_info = ''''''
# GitHub action运行需要填写对应的secrets
if "BARK" in os.environ and os.environ["BARK"]:
    BARK = os.environ["BARK"]
if "BARK_PUSH" in os.environ and os.environ["BARK_PUSH"]:
    BARK_PUSH = os.environ["BARK_PUSH"]
# 获取企业微信应用推送 QYWX_AM
if "QYWX_AM" in os.environ:
    if len(os.environ["QYWX_AM"]) > 1:
        QYWX_AM = os.environ["QYWX_AM"]
if "QYWX_KEY" in os.environ:
    if len(os.environ["QYWX_KEY"]) > 1:
        QYWX_KEY = os.environ["QYWX_KEY"]
        # print("已获取并使用Env环境 QYWX_AM")
if "PUSH_PLUS_TOKEN" in os.environ:
    if len(os.environ["PUSH_PLUS_TOKEN"]) > 1:
        PUSH_PLUS_TOKEN = os.environ["PUSH_PLUS_TOKEN"]
if "WXPUSH_TOKEN" in os.environ:
    if len(os.environ["WXPUSH_TOKEN"]) > 1:
        PUSH_PLUS_TOKEN = os.environ["WXPUSH_TOKEN"]

if BARK:
    notify_mode.append('bark')
    # print("BARK 推送打开")
if BARK_PUSH:
    notify_mode.append('bark')
    # print("BARK 推送打开")
if QYWX_AM:
    notify_mode.append('wecom_app')
    # print("企业微信机器人 推送打开")
if PUSH_PLUS_TOKEN:
    notify_mode.append('pushplus_bot')
    # print("微信推送Plus机器人 推送打开")
if WXPUSH_TOKEN:
    notify_mode.append('wxpusher')


def message(str_msg):
    global message_info
    print(str_msg)
    message_info = "{}\n{}".format(message_info, str_msg)
    sys.stdout.flush()


def bark(title, content):
    print("\n")
    if BARK:
        try:
            response = requests.get(
                f"""https://api.day.app/{BARK}/{title}/{urllib.parse.quote_plus(content)}""").json()
            if response['code'] == 200:
                print('推送成功！')
            else:
                print('推送失败！')
        except:
            print('推送失败！')
    if BARK_PUSH:
        try:
            response = requests.get(
                f"""{BARK_PUSH}/{title}/{urllib.parse.quote_plus(content)}""").json()
            if response['code'] == 200:
                print('推送成功！')
            else:
                print('推送失败！')
        except:
            print('推送失败！')
    print("bark服务启动")
    if BARK == '' and BARK_PUSH == '':
        print("bark服务的bark_token未设置!!\n取消推送")
        return


def pushplus_bot(title, content):
    try:
        print("\n")
        if not PUSH_PLUS_TOKEN:
            print("PUSHPLUS服务的token未设置!!\n取消推送")
            return
        print("PUSHPLUS服务启动")
        url = 'http://www.pushplus.plus/send'
        data = {
            "token": PUSH_PLUS_TOKEN,
            "title": title,
            "content": content,
            "topic": PUSH_PLUS_USER
        }
        body = json.dumps(data).encode(encoding='utf-8')
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        if response['code'] == 200:
            print('推送成功！')
        else:
            print('推送失败！')
    except Exception as e:
        print(e)


def wxpusher(title, content):
    try:
        if not WXPUSH_TOKEN:
            print("WXPUSHER服务的token未设置!!\n取消推送")
            return
        print("WXPUSHER服务启动")
        url = 'http://wxpusher.zjiecode.com/api/send/message'
        data = {
            "appToken": WXPUSH_TOKEN,
            "content": content,
            "summary": title,
            "contentType": 3,
            "topicIds": [WXPUSH_TOPIC],
        }
        response = requests.post(url=url, json=data).json()
        if response['code'] == 1000:
            print('推送成功！')
        else:
            print('推送失败！')
    except Exception as e:
        print(e)


def wecom_key(title, content):
    print("\n")
    if not QYWX_KEY:
        print("QYWX_KEY未设置!!\n取消推送")
        return
    print("QYWX_KEY服务启动")
    print("content" + content)
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": title + "\n" + content.replace("\n", "\n\n")
        }
    }
    print(f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={QYWX_KEY}")
    response = requests.post(f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={QYWX_KEY}", json=data,
                             headers=headers).json()
    print(response)


# 企业微信 APP 推送
def wecom_app(title, content):
    try:
        if not QYWX_AM:
            print("QYWX_AM 并未设置！！\n取消推送")
            return
        QYWX_AM_AY = re.split(',', QYWX_AM)
        if 4 < len(QYWX_AM_AY) > 5:
            print("QYWX_AM 设置错误！！\n取消推送")
            return
        corpid = QYWX_AM_AY[0]
        corpsecret = QYWX_AM_AY[1]
        touser = QYWX_AM_AY[2]
        agentid = QYWX_AM_AY[3]
        try:
            media_id = QYWX_AM_AY[4]
        except:
            media_id = ''
        wx = WeCom(corpid, corpsecret, agentid)
        # 如果没有配置 media_id 默认就以 text 方式发送
        if not media_id:
            message = title + '\n\n' + content
            response = wx.send_text(message, touser)
        else:
            response = wx.send_mpnews(title, content, media_id, touser)
        if response == 'ok':
            print('推送成功！')
        else:
            print('推送失败！错误信息如下：\n', response)
    except Exception as e:
        print(e)


class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid

    def get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': self.CORPID,
                  'corpsecret': self.CORPSECRET,
                  }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def send_text(self, message, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {
                "content": message
            },
            "safe": "0"
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "Author",
                        "content_source_url": "",
                        "content": message.replace('\n', '<br/>'),
                        "digest": message
                    }
                ]
            }
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]


def send(title, content):
    """
    使用 bark, telegram bot, dingding bot, serverJ 发送手机推送
    :param title:
    :param content:
    :return:
    """
    for i in notify_mode:
        if i == 'bark':
            if BARK or BARK_PUSH:
                bark(title=title, content=content)
            else:
                print('未启用 bark')
            continue
        elif i == 'wecom_app':
            if QYWX_AM:
                wecom_app(title=title, content=content)
            else:
                print('未启用企业微信应用消息推送')
            continue
        elif i == 'pushplus_bot':
            if PUSH_PLUS_TOKEN:
                pushplus_bot(title=title, content=content)
            else:
                print('未启用 PUSHPLUS机器人')
            continue
        elif i == 'wxpusher':
            if WXPUSH_TOKEN:
                wxpusher(title=title, content=content)
            else:
                print('未启用WXPUSHER消息推送')
            continue
        else:
            print('此类推送方式不存在')


class Zhubao:
    def __init__(self):
        self.headers = {
            'Accept': '*/*',
            'Access-Token': 'false',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=utf-8',
            'platform': 'H5',
            'Host': 'h5shop.duoxiezhubao.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1',
            'Referer': 'https://h5shop.duoxiezhubao.com/h5/',
            'storeId': '10001',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        self.url = 'https://h5shop.duoxiezhubao.com/index.php?s=/api/goods/list&categoryId=0&page='

    def get_totalpages(self):
        response = requests.get(self.url + '9', headers=self.headers)
        result = response.json()
        total_pages = list(range(1, result['data']['list']['last_page'] + 1))
        return total_pages

    def repertory(self):
        total_pages = self.get_totalpages()
        count = 0
        res = []
        list = []
        for page in total_pages:
            response = requests.get(self.url + str(page), headers=self.headers)
            data = response.json()
            res.append(data)
        for a in res:
            for i in a['data']['list']['data']:
                if i['stock_total'] != 0:
                    # msg.append(f"【{i['goods_name']}】库存：{i['stock_total']}  【价格】：{i['goods_price_max']}")
                    list.append(
                        {'goodsid': i['goods_id'], 'price': i['goods_price_min'], 'stock_total': i['stock_total'],
                         'msg': f"【价格】{i['goods_price_max']},【库存】{i['stock_total']},【链接】:https://h5shop.duoxiezhubao.com/h5/#/pages/goods/detail?goodsId={i['goods_id']};"})
        if LOCK_FLAG:
            for thing in list:
                price = float(thing['price'])
                if ((6000 <= price <= 12000) and count <= ORDER_LIMIT and self.fetch_order_list() <= ORDER_LIMIT):
                    self.submit_checkout(thing['goodsid'])
                    count += 1
        sorted_list = sorted(list, key=lambda x: x['price'], reverse=True)
        return sorted_list

    def submit_checkout(selff, goods_id):
        url = 'https://h5shop.duoxiezhubao.com/index.php?s=/api/checkout/submit'
        headers = {
            'storeId': '10001',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json;charset=utf-8',
            'Origin': 'https://h5shop.duoxiezhubao.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1',
            'platform': 'H5',
            'Access-Token': '4fb74f283af42b714b50d00ea9e8a04a',
            'Host': 'h5shop.duoxiezhubao.com',
            'Referer': 'https://h5shop.duoxiezhubao.com/h5/',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Accept': '*/*'
        }
        body = {
            "mode": "buyNow",
            "delivery": 10,
            "payType": 30,
            "couponId": 0,
            "isUsePoints": 0,
            "remark": "",
            "goodsId": goods_id,  # 可变参数传入的商品ID
            "goodsNum": "1",
            "goodsSkuId": "0"
        }

        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()  # 检查HTTP请求是否成功
            print(response.json())
        except requests.exceptions.RequestException as e:
            return None  # 发生错误时返回None

    def fetch_order_list(self):
        url = 'https://h5shop.duoxiezhubao.com/index.php?s=/api/order/list&dataType=payment&page=1'
        headers = {
            'storeId': '10001',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json;charset=utf-8',
            'Origin': 'https://h5shop.duoxiezhubao.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1',
            'platform': 'H5',
            'Access-Token': '4fb74f283af42b714b50d00ea9e8a04a',
            'Host': 'h5shop.duoxiezhubao.com',
            'Referer': 'https://h5shop.duoxiezhubao.com/h5/',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Accept': '*/*'
        }

        try:
            response = requests.get(url, headers=headers)
            res = response.json()
            return res['data']['list']['total']
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}')


if __name__ == '__main__':
    msg = ''
    zhubao = Zhubao()
    msgs = zhubao.repertory()
    if msgs:
        for m in msgs:
            msg += "\n" + m['msg']
        msg += f"\n复制链接到zfb打开进行锁单\n时间：{(datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')}"
        print(msg)
        send("珠宝库存通知", msg)





