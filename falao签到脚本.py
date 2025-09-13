import requests
import json
import time
import os
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

        # 从环境变量读取 Telegram 相关配置
        self.TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
        self.TG_CHAT_ID = os.getenv('TG_USER_ID')
    
    def _parse_accounts(self):
        accounts_str = os.getenv('BIRD_ACCOUNTS', '')
        if not accounts_str:
            print("❌ 错误：未设置环境变量 BIRD_ACCOUNTS")
            print("请设置账号列表，支持换行或@分割")
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
                return {'success': False,'error': f"HTTP {response.status_code}: {response.text[:100]}"}
        except Exception as e:
            return {'success': False,'error': str(e)}
    
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
                    return {'success': True,'message': f"签到成功！获得积分: {result.get('addcredit', '0')}",'data': data}
                else:
                    return {'success': False,'message': '签到失败','data': data}
            else:
                return {'success': False,'message': f"HTTP {response.status_code}",'error': response.text[:100]}
        except Exception as e:
            return {'success': False,'message': '请求异常','error': str(e)}
    
    def send_telegram_message(self, text):
        if not self.TG_BOT_TOKEN or not self.TG_CHAT_ID:
            print("❌ Telegram环境变量TG_BOT_TOKEN或TG_USER_ID未设置，跳过推送")
            return
        url = f"https://api.telegram.org/bot{self.TG_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": self.TG_CHAT_ID,
            "text": text
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print("✅ Telegram消息发送成功")
            else:
                print(f"❌ Telegram消息发送失败: {response.text}")
        except Exception as e:
            print(f"❌ 发送Telegram消息异常: {e}")
    
    def process_account(self, openid, index, total):
        log_lines = []
        log_lines.append(f"{'='*60}")
        log_lines.append(f"📱 处理账号 {index}/{total}: {openid[:10]}...")
        
        sign_info = self.get_sign_info(openid)
        if not sign_info['success']:
            err_msg = f"❌ 获取签到信息失败: {sign_info['error']}"
            log_lines.append(err_msg)
            self.send_telegram_message(err_msg)
            return False
        
        log_lines.append(f"👤 用户昵称: {sign_info['nickname']}")
        log_lines.append(f"💰 当前积分: {sign_info['myjindou']}")
        log_lines.append(f"📅 连续签到: {sign_info['lianxu']} 天")
        log_lines.append(f"📊 总签到: {sign_info['total']} 天")
        log_lines.append(f"✅ 今日已签到: {'是' if sign_info['signed'] else '否'}")
        
        if sign_info['signed']:
            info_msg = "ℹ️ 今日已签到，跳过"
            log_lines.append(info_msg)
            self.send_telegram_message(f"账号 {index}/{total} {openid[:10]}... {info_msg}")
            return True
        
        log_lines.append("🎯 执行签到...")
        sign_result = self.sign_in(openid)
        
        if sign_result['success']:
            success_msg = f"✅ 签到成功! {sign_result['message']}"
            log_lines.append(success_msg)
            self.send_telegram_message(f"账号 {index}/{total} {openid[:10]}... {success_msg}")
            return True
        else:
            fail_msg = f"❌ 签到失败: {sign_result['message']}"
            log_lines.append(fail_msg)
            if 'error' in sign_result:
                log_lines.append(f"   错误详情: {sign_result['error']}")
            self.send_telegram_message(f"账号 {index}/{total} {openid[:10]}... {fail_msg}")
            return False
    
    def run(self):
        print("🐦 小鸟签到脚本启动")
        print("=" * 60)
        
        if not self.accounts:
            print("❌ 没有配置账号，程序退出")
            return
        
        print(f"🎯 开始处理 {len(self.accounts)} 个账号")
        
        success_count = 0
        total_count = len(self.accounts)
        
        for i, openid in enumerate(self.accounts, 1):
            try:
                if self.process_account(openid, i, total_count):
                    success_count += 1
            
                if i < total_count:
                    print("⏳ 等待 2 秒...")
                    time.sleep(2)
                    
            except Exception as e:
                error_msg = f"❌ 处理账号 {openid[:10]}... 时出错: {e}"
                print(error_msg)
                self.send_telegram_message(error_msg)
        
        summary = (f"\n{'='*60}\n"
                   f"📊 签到结果汇总:\n"
                   f"✅ 成功: {success_count}/{total_count}\n"
                   f"❌ 失败: {total_count - success_count}/{total_count}\n"
                   f"📈 成功率: {success_count/total_count*100:.1f}%\n")
        print(summary)
        self.send_telegram_message(summary)
        
        if success_count == total_count:
            self.send_telegram_message("🎉 所有账号签到完成!")
        elif success_count > 0:
            self.send_telegram_message("⚠️ 部分账号签到成功")
        else:
            self.send_telegram_message("💥 所有账号签到失败")

def main():
    signer = BirdSignIn()
    signer.run()

if __name__ == "__main__":
    main()
