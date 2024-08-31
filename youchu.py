# -*- coding: utf-8 -*-
"""
cron: 6 0,12 * * *
new Env('邮储种树');
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

activity_id = '9e1ecafcd5380de88409ff26569ea518'

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
        if json.loads(response.text)['data'][i]['name'] =='yctoken':
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


class TaskCommitter:
    def __init__(self, token, activity_id):
        self.token = token
        self.activity_id = activity_id
        self.base_url = "https://m.ujia007.com/ujia_mall/api/"
        self.base_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://m.ujia007.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20D67 NebulaSDK/1.8.100112 Nebula Source/YOUBankApp/psbc UnionPay/1.0 PSBC/newPsbc WK PSDType(1) mPaaSClient/(null)',
            'Cookie': f'SESSION=YWFjYzY0ZmUtMjg5Yy00MTFlLTljNzQtMjVmOWYwZTA3Mzgx; POSAPP_token={self.token}; client=ujia_mall; customer_key=POSAPP; isFirstLogin=0; last_login_env=psBcApp; miniOpenId=; openid=; sessionid=aacc64fe-289c-411e-9c74-25f9f0e07381; stationId=218; stationKey=psbcAppForUser; token={self.token}; umengId=1281192848; userid=UJIAUSER221213162784847; station_umengId=1281192848; usertoken={self.token}; CNZZDATA1281192848=90733685-1722471363-%7C1724991375; acw_tc=784e2c9017249913506411518e1b9464ce7392b4142a6583c99c59a629b052; tfstk=fdFtQCToMpdqs1e0KP6nimv0ogGOZSUwRlzWimmMhkELxDvgoRXaRygSx5mgSfOfHlqAbAXamZELPuQqfGlgHKZuoC4isrVpDlqkixNmmSQx_W2MicjZMrZoHoIlZ_4a7blfqgA1NrdrGq1mcTWsYslqGgjhZ_4a7jroLk7kMy_KoqxslogXOw3-kjOshC9BADujGmZjGalw9mYxxIeXKhZwVyipGIUxWfi5aDdXGW39q0aOUIOb9VH_iKVWGQm7XrFZE59Ah2FTyS3UJTpSJ5U8MqFV06Iyguq8lw-o8XpOJS923Agn6f8BuVIEbiuKqwxM3KkOr2nlJwp23AgEJ0bUgKJqBaf..; UM_distinctid=19085a2661215ed-06f24901cfa7958-5012524f-51bf4-19085a266132bff',
            'Host': 'm.ujia007.com',
            'Referer': f'https://m.ujia007.com/ujia_mall/web/posActivity/tree/activity.html?activityId={self.activity_id}&customer_key=POSAPP&stationId=8d54292991d5e368&stationKey=psbcAppForUser&returnUrlKey=posTrees&loginSource=userCenter&uUserId=080601a344f10f7cde08fa978d3f94106585f87e441011fc&uSign=D615EA43F719E004C18460122FBA92BA&uTimesTamp=d4458a61359eadac762a750f23b2792f&isFirstLogin=0&token={self.token}',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Accept': '*/*'
        }

    def commit_task(self, task_code):
        url = self.base_url + "task/commitTask"
        body = {
            'token': self.token,
            'activityId': self.activity_id,
            'taskCode': task_code
        }
        response = requests.post(url, headers=self.base_headers, data=body)
        response_data = response.json()
        result = response_data['msg']
        return result


    def get_user_collect_task_list(self):
        url = self.base_url + "task/getUserCollectTaskList"
        body = {
            'token': self.token,
            'activityId': self.activity_id
        }
        response = requests.post(url, headers=self.base_headers, data=body)
        response_data = response.json()
        # 提取 taskCode 和 taskName 并存储在列表中
        task_list = response_data.get('data', [])
        tasks = [{'taskCode': task.get('taskCode'), 'taskName': task.get('taskName')} for task in task_list if 'taskCode' in task and 'taskName' in task]
        return tasks


    def get_task_user_num(self):
        url = self.base_url + "task/getTaskUserNum"
        body = {
            'token': self.token,
            'activityId': self.activity_id
        }
        response = requests.post(url, headers=self.base_headers, data=body)
        tree_id = response.json()['data']['treeId']
        tree_num = response.json()['data']['treesNum']
        return tree_id, tree_num


    def one_button_watering(self,tree_id):
        url = self.base_url + "task/oneButtonWatering"
        body = {
            'token': self.token,
            'activityId': self.activity_id,
            'treeId': tree_id
        }
        response = requests.post(url, headers=self.base_headers, data=body)
        response_data = response.json()
        if response_data['success']:
            msg = f"【一键浇水成功】：浇水{response_data['data']}g"
        else:
            msg = 'token失效'
        return msg


    def main(self):
        msg = ''
        try:
            tasks = self.get_user_collect_task_list()
            tree_id , tree_num = self.get_task_user_num()[0] , self.get_task_user_num()[1]
            msg += f"【当前树木数量】：{tree_num}\n"
            for task in tasks:
                msg += f"【{task['taskName']}任务】:{self.commit_task(task['taskCode'])}\n"
            msg += self.one_button_watering(tree_id)
        except :
            msg += "token失效，请更新token"
        return msg
# 使用示例
yc_tokens = get_token_userid()
for yc in yc_tokens:
    task_committer = TaskCommitter(yc, activity_id)
    msg = task_committer.main()
send("【邮储养树活动通知】",msg)


