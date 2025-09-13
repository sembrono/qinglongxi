# 当前脚本来自于http://script.345yun.cn脚本库下载！
注意：
1、入口：#小程序://同程旅行/bYEbDfg9lhkxI6H
2、抓https://cvg.17usoft.com任意请求体里的idenId

版本更新：
v1.0.0  2025-08-25 铁臂阿童木

⚠️【免责声明】
------------------------------------------
1、此脚本仅用于学习研究，不保证其合法性、准确性、有效性，请根据情况自行判断，本人对此不承担任何保证责任。
2、由于此脚本仅用于学习研究，您必须在下载后 24 小时内将所有内容从您的计算机或手机或任何存储设备中完全删除，若违反规定引起任何事件本人对此均不负责。
3、请勿将此脚本用于任何商业或非法目的，若违反规定请自行对此负责。
4、此脚本涉及应用与本人无关，本人对因此引起的任何隐私泄漏或其他后果不承担任何责任。
5、本人对任何脚本引发的问题概不负责，包括但不限于由脚本错误引起的任何损失和损害。
6、如果任何单位或个人认为此脚本可能涉嫌侵犯其权利，应及时通知并提供身份证明，所有权证明，我们将在收到认证文件确认后删除此脚本。
7、所有直接或间接使用、查看此脚本的人均应该仔细阅读此声明。本人保留随时更改或补充此声明的权利。一旦您使用或复制了此脚本，即视为您已接受此免责声明。
"""
import threading
import json
import os, sys, time, random
import requests
import re

title = "同程私域"
ckName = 'lpzl_tcsy'
host = "cvg.17usoft.com"
baseUrl = f"https://{host}"
api = {
    "get_user_info":baseUrl+"/activity/checkin/getIndexInfo",
    "get_tasks":baseUrl+"/activity/checkin/getClockinTaskInfo",
    "complete_task":baseUrl+"/activity/checkin/completeClockinTask",
    "collect":baseUrl+"/activity/checkin/collectClockinTaskRewardPoints",
    "get_qsPlayId":baseUrl+"/activity/checkin/getAttendLotteryInfo",
    "draw":baseUrl+"/activity/checkin/performLottery",
    "get_prize":baseUrl+"/activity/checkin/getLotteryPrize",
}
isThread = False #是否开启并发


class program:
    def __init__(self,ck):
        self.idenId = ck
        self.headers = {
            "content-type": "application/json",
            "accept": "application/json, text/plain, */*",
            "sec-fetch-site": "cross-site",
            "accept-language": "zh-CN,zh-Hans;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "sec-fetch-mode": "cors",
            "origin":"https://wx.17u.cn",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.188 Mobile Safari/537.36 XWEB/1260117 MMWEBSDK/20240501 MMWEBID/3169 MicroMessenger/8.0.50.2701(0x2800325B) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
            "referer": "https://wx.17u.cn",
            "sec-fetch-dest": "empty",
        }
        self.points = 0
        self.enShareKey = ''

    def get_user_info(self):
        url = api["get_user_info"]
        data = {
            "idenId": self.idenId,
            "pid": 501,
            "refId": "1000",
            "nick": "同程用户",
            "icon": "https://file.40017.cn/huochepiao/activity/20200521supplies/img/defaultImg-fs8.png"
        }
        try:
            response = requests.post(url=url, headers=self.headers, json=data, timeout=30)
            rs = response.json()
        except Exception as e:
            print(f'请求失败: {e}')
            rs = None
        if rs:
            if rs['code'] == 1000:
                self.points = rs['data']['points']
                self.enShareKey = rs['data']['enShareKey']
            else:
                print(f'用户信息获取失败：{rs["message"]}')

    def get_tasks(self,type=1):
        url = api["get_tasks"]
        data = {
            "idenId": self.idenId,
            "pid": 501,
            "refId": "1000",
            "nick": "同程用户",
            "icon": "https://file.40017.cn/huochepiao/activity/20200521supplies/img/defaultImg-fs8.png"
        }
        try:
            response = requests.post(url=url, headers=self.headers, json=data, timeout=30)
            rs = response.json()
        except Exception as e:
            print(f'请求失败: {e}')
            rs = None
        if rs:
            if rs['code'] == 1000:
                if type == 1:
                    return rs['data']['taskList']
                else:
                    return rs['data']['waitCollectPointsTaskList']
        return None

    def complete_task(self,taskType,rewardPoints):
        url = api["complete_task"]
        data = {
            "idenId": self.idenId,
            "pid": 501,
            "refId": "1000",
            "nick": "同程用户",
            "icon": "https://file.40017.cn/huochepiao/activity/20200521supplies/img/defaultImg-fs8.png",
            "taskType": taskType,
            "rewardPoints": rewardPoints
        }
        try:
            response = requests.post(url=url, headers=self.headers, json=data, timeout=30)
            rs = response.json()
        except Exception as e:
            print(f'请求失败: {e}')
            rs = None
        if rs:
            if rs['code'] == 1000:
                print('任务完成✅')
            else:
                print(f'任务失败❌：{rs["message"]}')

    def collect(self,completeTaskId,title,points):
        url = api["collect"]
        data = {
            "idenId": self.idenId,
            "pid": 501,
            "refId": "1000",
            "nick": "同程用户",
            "icon": "https://file.40017.cn/huochepiao/activity/20200521supplies/img/defaultImg-fs8.png",
            "completeTaskId": completeTaskId
        }
        try:
            response = requests.post(url=url, headers=self.headers, json=data, timeout=30)
            rs = response.json()
        except Exception as e:
            print(f'请求失败: {e}')
            rs = None
        if rs:
            if rs['code'] == 1000:
                print(f'奖励【{title}】获取成功:{points}萌力值')

    def do_task(self):
        tasks = self.get_tasks()
        if tasks:
            for task in tasks:
                if task['couldComplete']:
                    complete_times = task['maxCompleteTimesPerDay'] - task['completeTimesToday']
                    if complete_times > 0:
                        for i in range(complete_times):
                            print(f'开始执行第 {i+1} 次【{task["title"]}】')
                            self.complete_task(task['type'],task['rewardPoints'])
                            time.sleep(10)
                else:
                    print(f'【{task["title"]}】✅')

        collect_list = self.get_tasks(2)
        if collect_list:
            for collect in collect_list:
                self.collect(collect['id'],collect['title'],collect['rewardPoints'])

    def get_qsPlayId(self):
        url = api["get_qsPlayId"]
        data = {
            "idenId": self.idenId,
            "pid": 501,
            "refId": "1000",
            "nick": "同程用户",
            "icon": "https://file.40017.cn/huochepiao/activity/20200521supplies/img/defaultImg-fs8.png"
        }
        try:
            response = requests.post(url=url, headers=self.headers, json=data, timeout=30)
            rs = response.json()
        except Exception as e:
            print(f'请求失败: {e}')
            rs = None
        if rs:
            if rs['code'] == 1000:
                return rs['data']['qsPlayId']
        return None

    def draw(self,qsPlayId):
        url = api["draw"]
        data = {
            "idenId": self.idenId,
            "pid": 501,
            "refId": "1000",
            "nick": "同程用户",
            "icon": "https://file.40017.cn/huochepiao/activity/20200521supplies/img/defaultImg-fs8.png",
            "qsPlayId": qsPlayId
        }
        try:
            response = requests.post(url=url, headers=self.headers, json=data, timeout=30)
            rs = response.json()
        except Exception as e:
            print(f'请求失败: {e}')
            rs = None
        if rs:
            if rs['code'] == 1000:
                print('抽奖成功✅')
            else:
                print(f'抽奖失败❌：{rs["message"]}')

    def do_draw(self):
        if self.points >= 100:
            draw_times = self.points//100
            for i in range(draw_times):
                qsPlayId = self.get_qsPlayId()
                if not qsPlayId:
                    print('抽奖id获取失败')
                else:
                    self.draw(qsPlayId)
                    time.sleep(1)

    def get_prize(self):
        url = api["get_prize"]
        data = {
            "idenId": self.idenId,
            "pid": 501,
            "refId": "1000",
            "nick": "同程用户",
            "icon": "https://file.40017.cn/huochepiao/activity/20200521supplies/img/defaultImg-fs8.png"
        }
        try:
            response = requests.post(url=url, headers=self.headers, json=data, timeout=30)
            rs = response.json()
        except Exception as e:
            print(f'请求失败: {e}')
            rs = None
        if rs:
            if rs['code'] == 1000 and rs['data']:
                print(f'中奖记录：')
                for prize in rs['data']:
                    print(f'{prize["title"]}  {prize["createTime"]}')


    def task(self):
        if not isThread:
            sleepTime = random.randint(60,600)
            print(f'延迟{sleepTime}秒执行...')
            # time.sleep(sleepTime)
        self.get_user_info()
        print(f'执行前萌力值:{self.points}')
        """执行任务"""
        self.do_task()

        self.get_user_info()
        print(f'执行后萌力值:{self.points}')
        """抽奖"""
        self.do_draw()

        """查询奖励记录"""
        self.get_prize()

def run_program(ck):
    main_program = program(ck)
    main_program.task()

if __name__ == '__main__':
    if os.environ.get(ckName):
        ck = os.environ.get(ckName)
    else:
        ck = ""
        if ck == "":
            print("请设置变量")
            sys.exit()

    cks = re.split(r'[&\n]', ck)

    print(f"{' ' * 10}꧁༺ {title} ༻꧂\n")

    if isThread:
        threads = []

        for i, ck in enumerate(cks):
            try:
                thread = threading.Thread(target=run_program, args=(ck,))
                threads.append(thread)
                thread.start()
            except Exception as e:
                print(e)

        for thread in threads:
            thread.join()
    else:
        for i, ck in enumerate(cks):
            try:
                print(f'\n----------- 🎊 第 {i + 1} 个账号 🎊 -----------\n')
                main = program(ck)
                main.task()
            except Exception as e:
                print(e)



    print(f'\n----------- 🎊 执 行  结 束 🎊 -----------\n')
# 当前脚本来自于http://script.345yun.cn脚本库下载！