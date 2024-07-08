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
import threading

CouponIdList = {'Ten':'d%3dyAPPsbBvvy%26trans_rule_biz_id%3dwKtrans_rule_i',
                'Fourteen':'d%3dyAPPsbBvva%26trans_rule_biz_id%3dwKtrans_rule_i'}
def send_post_request(token, couponid):
    url = "https://wx.waimai.meituan.com/mtiphone_wmgroup/v1/wlwc/exchangeredenvelopes?ui=3428020707&region_id=1000360100&region_version=1709695482084&csecpkgname=com.meituan.itakeaway&csecplatform=2&csecversion=1.0.15&csecversionname=8.30.1"
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'R2X-Referer': 'https://servicewechat.com/wx2c348cf579062e56/0/page-frame.html',
        'Host': 'wx.waimai.meituan.com',
        'mtgsig': '{"a0":"3.0","a1":"7db5788e-97df-40d7-a19c-1cb62ef9f257","a3":24,"a4":1720118368,"a5":"B4Oji2EVUzXf16wtjPjcfw+iNDn/BI9+N1+rCqOMLQp6GOXbiQUCCs9z5g0xb1N8zP9FnDD1weWybG9GzbPyHTMfF8oFgaeNjFEDr67UC/p6XpdzYxJXFwzHMhGz3wZPIl/ucCq/RFoCnJ7SgsfFumqYi2FttxTZ2S67x2Fv7fKoanBBwZnTtJxa0ZMfF1jJA+DR7Nb5G84ogr1BNsNHAGmJY5eochhYitAh8rzWxpyqpNKwBh1lRY9C2rtM7K5qcCMZTL15hJjQNBr3M53qmzwT7/N2Lly9hqvSXFdMKCwSQqCCKmt145oHiKztSs/H5DP5sctlvtjbTayCegINXQQkD7etaE9HXvtE1MFH1M/7qz8UaBJUmU6z3KxRYtVBseICokY=","a6":0,"a7":"eds42u5pcGhV66/4G6/or/e+unyxpPmhXqAVD6IBK7VPomVH0qhiqAdyVznmmM8UujnhZKnauNWPokTuBrdnUmwZmi8+AkhI1XJ7T9hycHs=","a8":"05e564299db7499b9c36902e570c59c46457f218cff3b8a9353ba784","a9":"a1eddb21eV2Ts9/0Joo1EuL97IFi9jn9tNz8Y+SdzZcg/guKpsSmlCgeSz7Fk8xTMb/MDxAP/smcImSdlt4aRdnjqXZgwJq4Rn7BpXVkoqDxdehmWwWldgejSRf+JhrkEHD3y8ailvmv7AbF2PqQbEBNfWH0uzMROLjMAQzT1RNeUk/lCNDAmGxuuLa66UP0yUrRWqyJvXqr1Yj7+tpTJr8d32Axj1ygfG55ShexZ1uVM0xPRcWVvC87h4scU7dokru4XVMPuwim9Z8sF0rJEmGl7RX7t1E2JYhW1MfcWwDN6inRJTgG5e4yNVEPaBXT+OYeCg5AKj1l2O7VwtrD2u2RWjgcgFyQydIvcUT2YM76qvL4FRYtXfaX24+4vQxpJRGGtCqjMQHJtZ4j9WcpWLi1iCM6RGxrJgFfwlVbkEN32iqP4JUUAO+aPvrh4s5QzkNEnkQdiXD2ElQoJXKarGXV8o3qmHfbGPm+R7PF8KJf6FPFLjDXayqQ4WC7w+xKGtttKT8rKxHRQhRfiNn9oFOGVT3G71wofN4g60ConnhDnVz62UMIUOclgINsiU1uBMl/O16xjkyj84WAKJmL3T9lcajuXWo7xrJcYHaxusQiMNq9pCltA2Ty16bppQ0eF21iwvCoEflrIpZRwTef3Lvj69FaKhWBIS0dIbGlPIehsEnaTkeziqiEKxwGWj6/TJz1N1QN","a10":"5,96,1.1.6","x0":2,"a2":"54eb66070bc45d737df14cbc9e18a2ba"}',
        'Connection': 'keep-alive',
        'uuid': '0000000000000F500E5DA05094FB9B095EC62DD1197ADA170315197635030298',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148  MicroMessenger/6.5.7 miniprogram MMP/1.17.1.43.7 MSC/1.43.7 waimai/8.30.1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://mmp.meituan.com/b75b8f2e8db84d05/9.51.6/service',
        'yodaReady': 'native',
        'wm-ctype': 'wxapp',
        'csecuuid': '0000000000000F500E5DA05094FB9B095EC62DD1197ADA170315197635030298',
        'token': token,
        'Accept': '*/*',
        'csecuserid': '3428020707',
        'Dj-Token': 'BUtNUwMAAABuBktNUwMaOQIAAAABO5rMWgAAACxUk3kku9S+/FhNj6KAztMR9mlxIrC/udidqTpxbVgrQKyl7zdA3lhQZFaStCIshwoQjlREMTO5DKykeRypZE7g0lAW3xPvzwmWI3j6ZxjP7hBgLBiRBGiGW5YAAACTi3RZJJ6PRNROc6wapx+QijEAZXKZLVRACB2kLzWOx/nClfmYOn6Qw/eeSBu2IM/ZgRDfW+/rQi6ISUgrAWEknnwXBlI5JtmET18h7efSqwbqJk2XNVVAFEcXUHul50csEFkwTHxJt0iT8zPzNEW/JAsglaMKW44iKQHxuFZwCiui6OVxyYB0IF90CIRoXK9wufvG',
        'yodaVersion': '1.14.107.6',
        'Cookie': f'network=wifi; WEBDFPID=371z3z2uwvz452u2194u7v5v2vuvx32v81uz1y7v9749795870xzv3x6-2031882246177-1716522246177QKOGICS868c0ee73ab28e1d0b03bc83148500061320; _lx_utm=utm_campaign%3DAwaimaiBwaimaiGhomepage_category_9_108616_(null)H0%26utm_content%3D0000000000000F500E5DA05094FB9B095EC62DD1197ADA170315197635030298%26utm_medium%3Diphone%26utm_source%3D2000%26utm_term%3D8.30.1; _lxsdk_s=1907f0a74a5-950-d77-def%7C%7CNaN; _utm_campaign=AwaimaiBwaimaiH0; _utm_content=0000000000000F500E5DA05094FB9B095EC62DD1197ADA170315197635030298; _utm_medium=iphone; _utm_source=2000; _utm_term=8.30.1; cityid=83; dpid=; token={token}; uuid=0000000000000F500E5DA05094FB9B095EC62DD1197ADA170315197635030298; lt=AgFwKbEmlQ0sSLacdO-NOjvi1KZITtjRNPd_Ygy498nzF3Bonlk0KUDDtIlqAvapvwYEVlXxI4nVHREAAADvIAAA6zPim4L_vTLZQSw_PHC3nTBsOxv5BndGd2yB-xaPzvZbM2EbdpXuVL7FqeYHUnof22K74-Em05OTCccnEmci1g; n=Accont1652; isUuidUnion=true; iuuid=0000000000000F500E5DA05094FB9B095EC62DD1197ADA170315197635030298; ins_city_id=83; ins_city_name=%E5%8D%97%E6%98%8C; fd_maidan_accessno=; fd_yuefu_open_type=H5; userId=3428020707; fd_maidan_skipLandingAndResult=; fd_maidan_utm_source=creditpay_app-fup-assetDebt_787570; is_from_feed=; maidan_utm_source=creditpay_app-fup-assetDebt_787570; ta.uuid=1793850545389068353; _lxsdk=0000000000000F500E5DA05094FB9B095EC62DD1197ADA170315197635030298; _lxsdk_cuid=18fa8b29915c8-01d8759475b4768-56443107-51bf4-18fa8b29916c8; _lxsdk_dpid=f500e5da05094fb9b095ec62dd1197ada170315197635030298; _lxsdk_unoinid=f500e5da05094fb9b095ec62dd1197ada170315197635030298'
    }

    body = f'wm_dtype=iPhone%2014%20Pro%3CiPhone15%2C2%3E&wm_dversion=6.6.3&wm_dplatform=iOS&wm_uuid=0000000000000F500E5DA05094FB9B095EC62DD1197ADA170315197635030298&wm_visitid=755719b4-d452-4e16-ad93-c9b7b3051d11&wm_appversion=9.51.6&wm_logintoken={token}&userToken={token}&req_time=1720118368374&waimai_sign=%2F&userid=3428020707&user_id=3428020707&lch=1000&sessionId=DTRLPJ&province=%E6%B1%9F%E8%A5%BF%E7%9C%81&nickName=None&gender=0&country=%E4%B8%AD%E5%9B%BD&city=%E5%8D%97%E6%98%8C&optimusCode=20&riskLevel=71&partner=4&platform=13&uuid=0000000000000F500E5DA05094FB9B095EC62DD1197ADA170315197635030298&open_id=3428020707&rc_app=4&rc_platform=13&mtSecuritySiua=true&mtSecuritySign=true&host_version=8.30.1&fpApp=4&fpPlatform=5&host_ctype=iphone&wm_uuid_source=client&sdkVersion=2.2.6&wxPrint=&wxNickName=None&pageType=1&djEncryptRiskData=true&newUserCoupon=0&tradeSource=33&exchangeCoinNumber=200&exchangeRuleId={couponid}&city_id_level2=360100&city_id_level3=360105&actual_city_id_level2=360100&actual_city_id_level3=360105&app_model=4&rank_list_id=134d941d610e8a1245d7a51976350302&wm_ctype=mtiphone_wmgroup'

    for _ in range(4):  # 执行三次请求
        response = requests.post(url, json=body, headers=headers)
        response = requests.post(url, data=body, headers=headers)
        res = response.json()
        print(res)
 

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
        if json.loads(response.text)['data'][i]['name'] =='mt':
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
    
def main():
    tokens = get_token_userid()
    # 获取当前时间
    current_hour = datetime.now().hour
    # 根据当前时间选择couponid
    if 8 <= current_hour < 10:  # 如果当前时间接近10点
        couponid = CouponIdList['Ten']
    elif 12 <= current_hour < 14:  # 如果当前时间接近14点
        couponid = CouponIdList['Fourteen']
    else:
        couponid = CouponIdList['Ten']  # 其他时间段可以选择默认值或者不赋值

    chunk_size = 4  # 每次取出的token数量
    for i in range(0, len(tokens), chunk_size):
        tokens_to_use = tokens[i:i+chunk_size]  # 取出当前chunk_size个token

        threads = []
        for token in tokens_to_use:
            thread = threading.Thread(target=send_post_request, args=(token, couponid))
            threads.append(thread)
            thread.start()

        # 等待所有线程执行完毕
        for thread in threads:
            thread.join()

if __name__ == "__main__":
    main()



