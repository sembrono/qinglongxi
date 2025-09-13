import os
import glob
import requests
import time
from datetime import datetime

class BirdSignIn:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = os.getenv('BIRD_BASE_URL', 'https://cloudprint.chongci.shop')
        self.accounts = self._parse_accounts()
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c2c)XWEB/8518',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'Accept-Language': '*',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://servicewechat.com/wx7d1787ad17f2d932/19/page-frame.html',
            'Accept-Encoding': 'gzip, deflate, br',
            'xweb_xhr': '1'
        }
        self.session.headers.update(self.headers)

        self.TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
        self.TG_CHAT_ID = os.getenv('TG_USER_ID')
        if not self.TG_BOT_TOKEN or not self.TG_CHAT_ID:
            print("❌ Telegram 环境变量 TG_BOT_TOKEN 或 TG_USER_ID 未设置")

        self.all_logs = []

    def _parse_accounts(self):
        accounts_str = os.getenv('BIRD_ACCOUNTS', '')
        if not accounts_str:
            print("❌ 错误：未设置环境变量 BIRD_ACCOUNTS")
            return []
        if '\n' in accounts_str:
            accounts = [acc.strip() for acc in accounts_str.split('\n') if acc.strip()]
        elif '@' in accounts_str:
            accounts = [acc.strip() for acc in accounts_str.split('@') if acc.strip()]
        else:
            accounts = [accounts_str.strip()]
        print(f"📋 解析到 {len(accounts)} 个账号")
        return accounts

    def get_sign_info(self, openid):
        url = f"{self.base_url}/app/index.php"
        params = {
            'i': '2',
            'c': 'entry',
            'm': 'ewei_shopv2',
            'do': 'mobile',
            'r': 'sign',
            'app': '1',
            'openid': openid
        }
        try:
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': data,
                    'nickname': data.get('nickname', 'N/A'),
                    'myjindou': data.get('myjindou', 'N/A'),
                    'lianxu': data.get('lianxu', 'N/A'),
                    'total': data.get('total', 'N/A'),
                    'signed': data.get('signed', 0)
                }
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}: {response.text[:100]}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def sign_in(self, openid):
        url = f"{self.base_url}/app/index.php"
        params = {
            'i': '2',
            'c': 'entry',
            'm': 'ewei_shopv2',
            'do': 'mobile',
            'r': 'sign.dosign',
            'app': '1',
            'openid': openid
        }
        try:
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 1:
                    result = data.get('result', {})
                    return {'success': True, 'message': f"签到成功！获得积分: {result.get('addcredit', '0')}"}
                else:
                    return {'success': False, 'message': '签到失败', 'data': data}
            else:
                return {'success': False, 'message': f"HTTP {response.status_code}"}
        except Exception as e:
            return {'success': False, 'message': '请求异常', 'error': str(e)}

    def process_account(self, openid, index, total):
        log_lines = []
        log_lines.append(f"账号 {index}/{total} {openid[:10]}...")
        sign_info = self.get_sign_info(openid)
        if not sign_info['success']:
            err_msg = f"获取签到信息失败: {sign_info['error']}"
            log_lines.append(err_msg)
            self.all_logs.append('\n'.join(log_lines))
            return False
        log_lines.append(f"昵称: {sign_info['nickname']}")
        log_lines.append(f"积分: {sign_info['myjindou']}")
        log_lines.append(f"连续签到: {sign_info['lianxu']} 天")
        log_lines.append(f"总签到: {sign_info['total']} 天")
        log_lines.append(f"今日已签到: {'是' if sign_info['signed'] else '否'}")
        if sign_info['signed']:
            info_msg = "今日已签到，跳过"
            log_lines.append(info_msg)
            self.all_logs.append('\n'.join(log_lines))
            return True
        log_lines.append("执行签到...")
        sign_result = self.sign_in(openid)
        if sign_result['success']:
            success_msg = f"签到成功! {sign_result['message']}"
            log_lines.append(success_msg)
            self.all_logs.append('\n'.join(log_lines))
            return True
        else:
            fail_msg = f"签到失败: {sign_result.get('message', '')}"
            log_lines.append(fail_msg)
            if 'error' in sign_result:
                log_lines.append(f"错误详情: {sign_result['error']}")
            self.all_logs.append('\n'.join(log_lines))
            return False

    def send_telegram_message(self, text):
        if not self.TG_BOT_TOKEN or not self.TG_CHAT_ID:
            print("Telegram 环境变量未配置，跳过推送消息")
            return
        url = f"https://api.telegram.org/bot{self.TG_BOT_TOKEN}/sendMessage"
        # 只发送一条消息，内容超长则截断
        max_len = 4096
        text_to_send = text[:max_len]
        payload = {
            "chat_id": self.TG_CHAT_ID,
            "text": text_to_send,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print("Telegram消息发送成功")
            else:
                print(f"Telegram消息发送失败: {response.text}")
        except Exception as e:
            print(f"发送Telegram消息异常: {e}")

    def read_and_push_latest_log(self, content_limit=2000):
        log_base_dir = "/ql/data/log"
        current_script_name = os.path.splitext(os.path.basename(__file__))[0]
        task_dirs = glob.glob(os.path.join(log_base_dir, f"{current_script_name}*"))
        if not task_dirs:
            err = f"未找到[{current_script_name}]相关日志文件夹"
            print(err)
            self.all_logs.append(err)
            return
        latest_task_dir = max(task_dirs, key=os.path.getctime)
        all_files = [os.path.join(latest_task_dir, f) for f in os.listdir(latest_task_dir) if os.path.isfile(os.path.join(latest_task_dir, f))]
        if not all_files:
            err = f"文件夹[{latest_task_dir}]内无文件"
            print(err)
            self.all_logs.append(err)
            return
        latest_log_file = max(all_files, key=os.path.getctime)
        print(f"正在读取文件：{latest_log_file}")
        try:
            try:
                with open(latest_log_file, "r", encoding="utf-8", errors="ignore") as f:
                    log_content = f.read()[:content_limit]
            except:
                with open(latest_log_file, "r", encoding="gbk", errors="ignore") as f:
                    log_content = f.read()[:content_limit]
            log_time = datetime.fromtimestamp(os.path.getctime(latest_log_file)).strftime("%Y-%m-%d %H:%M")
            self.all_logs.append(f"【{current_script_name}】_ {log_time}\n{log_content}")
        except Exception as e:
            err = f"读取失败：{str(e)}"
            print(err)
            self.all_logs.append(err)

    def run(self):
        print("冲刺鸭云印签到脚本启动")
        if not self.accounts:
            print("未找到任何账号，退出")
            return
        success_count = 0
        total_count = len(self.accounts)
        for i, openid in enumerate(self.accounts, 1):
            try:
                if self.process_account(openid, i, total_count):
                    success_count += 1
                if i < total_count:
                    time.sleep(2)
            except Exception as e:
                error_msg = f"处理账号 {openid[:10]} 时出错: {e}"
                print(error_msg)
                self.all_logs.append(error_msg)
        summary = (f"\n签到结果汇总:\n"
                   f"成功: {success_count}/{total_count}\n"
                   f"失败: {total_count - success_count}/{total_count}\n"
                   f"成功率: {success_count/total_count*100:.1f}%\n")
        print(summary)
        self.all_logs.append(summary)
        if success_count == total_count:
            self.all_logs.append("所有账号签到完成!")
        elif success_count > 0:
            self.all_logs.append("部分账号签到成功")
        else:
            self.all_logs.append("所有账号签到失败")

        self.read_and_push_latest_log()

        # 只发送一条消息，内容可能被截断
        final_message = "\n\n".join(self.all_logs)
        self.send_telegram_message(final_message)

def main():
    signer = BirdSignIn()
    signer.run()

if __name__ == "__main__":
    main()
