# 当前脚本来自于http://script.345yun.cn脚本库下载！
# 环境变量配置：
# - BIRD_ACCOUNTS: 账号列表，支持换行或@分割
#   格式1: openid1\nopenid2\nopenid3
#   格式2: openid1@openid2@openid3
#   活动地址：https://file.52bin.cn/img/ID9/202509/68c4aa8be873b.jpg

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
    
    def _parse_accounts(self):
        """解析账号列表"""
        accounts_str = os.getenv('BIRD_ACCOUNTS', '')
        if not accounts_str:
            print("❌ 错误：未设置环境变量 BIRD_ACCOUNTS")
            print("请设置账号列表，支持换行或@分割")
            return []
        
        # 支持换行和@分割
        if '\n' in accounts_str:
            accounts = [acc.strip() for acc in accounts_str.split('\n') if acc.strip()]
        elif '@' in accounts_str:
            accounts = [acc.strip() for acc in accounts_str.split('@') if acc.strip()]
        else:
            accounts = [accounts_str.strip()]
        
        print(f"📋 解析到 {len(accounts)} 个账号")
        return accounts
        
    def get_sign_info(self, openid):
        """获取签到信息"""
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
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text[:100]}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def sign_in(self, openid):
        """执行签到"""
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
                    return {
                        'success': True,
                        'message': f"签到成功！获得积分: {result.get('addcredit', '0')}",
                        'data': data
                    }
                else:
                    return {
                        'success': False,
                        'message': '签到失败',
                        'data': data
                    }
            else:
                return {
                    'success': False,
                    'message': f"HTTP {response.status_code}",
                    'error': response.text[:100]
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': '请求异常',
                'error': str(e)
            }
    
    def process_account(self, openid, index, total):
        """处理单个账号"""
        print(f"\n{'='*60}")
        print(f"📱 处理账号 {index}/{total}: {openid[:10]}...")
        
        # 1. 获取签到信息
        print("📋 获取签到信息...")
        sign_info = self.get_sign_info(openid)
        
        if not sign_info['success']:
            print(f"❌ 获取签到信息失败: {sign_info['error']}")
            return False
        
        print(f"👤 用户昵称: {sign_info['nickname']}")
        print(f"💰 当前积分: {sign_info['myjindou']}")
        print(f"📅 连续签到: {sign_info['lianxu']} 天")
        print(f"📊 总签到: {sign_info['total']} 天")
        print(f"✅ 今日已签到: {'是' if sign_info['signed'] else '否'}")
        
        if sign_info['signed']:
            print("ℹ️ 今日已签到，跳过")
            return True
        
        print("🎯 执行签到...")
        sign_result = self.sign_in(openid)
        
        if sign_result['success']:
            print("✅ 签到成功!")
            return True
        else:
            print(f"❌ 签到失败: {sign_result['message']}")
            if 'error' in sign_result:
                print(f"   错误详情: {sign_result['error']}")
            return False
    
    def run(self):
        """运行主程序"""
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
                print(f"❌ 处理账号 {openid[:10]}... 时出错: {e}")
        
        print(f"\n{'='*60}")
        print("📊 签到结果汇总:")
        print(f"✅ 成功: {success_count}/{total_count}")
        print(f"❌ 失败: {total_count - success_count}/{total_count}")
        print(f"📈 成功率: {success_count/total_count*100:.1f}%")
        
        if success_count == total_count:
            print("🎉 所有账号签到完成!")
        elif success_count > 0:
            print("⚠️ 部分账号签到成功")
        else:
            print("💥 所有账号签到失败")

def main():
    """主函数"""
    signer = BirdSignIn()
    signer.run()

if __name__ == "__main__":
    main()
import os
import glob
import requests
from datetime import datetime

# 从环境变量中读取 Telegram 机器人Token和用户ID
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_USER_ID = os.getenv("TG_USER_ID")
if not TG_BOT_TOKEN or not TG_USER_ID:
    raise ValueError("请在环境变量中设置 TG_BOT_TOKEN 和 TG_USER_ID")

def push_to_tg(script_name, log_time, log_content):
    title = f"【{script_name}】_ {log_time}"
    msg = f"{title}\n\n{log_content}"
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_USER_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"✅ TG推送成功: {title}")
        else:
            print(f"❌ TG推送失败，状态码: {response.status_code}, 内容: {response.text}")
    except Exception as e:
        print(f"❌ TG推送异常: {str(e)}")

def read_and_push_latest_log(task_name_prefix, script_name, content_limit=2000):
    log_base_dir = "/ql/data/log"
    if not os.path.exists(log_base_dir):
        err = "❌ 青龙日志根目录不存在：/ql/data/log"
        print(err)
        return err
    
    task_dirs = glob.glob(os.path.join(log_base_dir, f"{task_name_prefix}*"))
    if not task_dirs:
        err = f"❌ 未找到[{task_name_prefix}]相关日志文件夹"
        print(err)
        return err
    
    latest_task_dir = max(task_dirs, key=os.path.getctime)
    all_files = [os.path.join(latest_task_dir, f) for f in os.listdir(latest_task_dir) if os.path.isfile(os.path.join(latest_task_dir, f))]
    if not all_files:
        err = f"❌ 文件夹[{latest_task_dir}]内无文件"
        print(err)
        return err
    
    latest_log_file = max(all_files, key=os.path.getctime)
    print(f"✅ 正在读取文件：{latest_log_file}")
    try:
        try:
            with open(latest_log_file, "r", encoding="utf-8", errors="ignore") as f:
                log_content = f.read()[:content_limit]
        except:
            with open(latest_log_file, "r", encoding="gbk", errors="ignore") as f:
                log_content = f.read()[:content_limit]
        
        log_time = datetime.fromtimestamp(os.path.getctime(latest_log_file)).strftime("%Y-%m-%d %H:%M")
        push_to_tg(script_name, log_time, log_content)
        
        return (
            f"✅ 内容读取完成\n"
            f"📄 读取文件：{latest_log_file}\n"
            f"📝 推送内容长度：{len(log_content)}字符\n"
            f"📱 已推送【{script_name}_信息_{log_time}】到Telegram"
        )
    except Exception as e:
        err = f"❌ 读取失败：{str(e)}"
        print(err)
        return err

if __name__ == "__main__":
    current_script_name = os.path.splitext(os.path.basename(__file__))[0]
    result = read_and_push_latest_log(task_name_prefix=current_script_name, script_name=current_script_name)
    print(result)
