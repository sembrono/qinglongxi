import requests
import time
import os
from datetime import datetime
import json

# GLaDOS 多账号自动签到脚本(青龙环境适配)
# 环境变量配置:GLaDOS_CK,多账号用【回车】分隔,单账号格式:Cookie#Authorization
# Cookie格式:koa:sess=xxx; koa:sess.sig=xxx(多字段用; 分隔)
# https://glados.space/landing/EQYDX-78A5V-S9VXS-25CYB网站首页该机场采用邀请注册制 
#EQYDX-78A5V-S9VXS-25CYB邀请码  新用户注册 双方可获得15天免费会员时长
#好像签到可以获得Authorization
# 该脚本实现自动化签到 每签到100积分可自动兑换15天免费会员时长

class GLaDOSAutoCheckin:
    def __init__(self, cookies_dict, authorization, account_idx):
        """初始化:传入单账号的Cookie字典、Authorization、账号序号(用于日志区分)"""
        self.account_idx = account_idx  # 账号序号(如第1个账号、第2个账号)
        self.base_url = "https://glados.rocks"
        self.checkin_url = f"{self.base_url}/api/user/checkin"
        self.console_url = f"{self.base_url}/console"
        self.user_status_url = f"{self.base_url}/api/user/status"
        self.clash_url_template = "https://update.glados-config.com/mihomo/{userId}/{code}/{port}/glados.yaml"

        # 初始化会话与请求头
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": authorization,
            "Origin": self.base_url,
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty"
        }
        self.session.headers.update(self.headers)
        self.session.cookies.update(cookies_dict)

    def log_prefix(self):
        """生成日志前缀(含时间、账号序号),便于区分多账号"""
        return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [账号{self.account_idx}]"

    def test_login_status(self):
        """测试单账号登录状态"""
        try:
            response = self.session.get(self.console_url, allow_redirects=False, timeout=10)
            if response.status_code == 200:
                print(f"{self.log_prefix()} ✅ Cookie有效,登录正常")
                return True
            elif response.status_code == 302:
                print(f"{self.log_prefix()} ❌ Cookie过期/无效,需重新配置")
                return False
            else:
                print(f"{self.log_prefix()} ⚠️ 登录状态未知,响应码:{response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"{self.log_prefix()} ❌ 登录测试失败:{str(e)}")
            return False

    def get_user_info(self):
        """获取单账号个人信息+生成Clash链接"""
        if not self.test_login_status():
            return False

        try:
            print(f"\n{self.log_prefix()} 📱 开始获取个人信息...")
            response = self.session.get(self.user_status_url, timeout=15)
            response.encoding = "utf-8"
            result = response.json()

            if response.status_code == 200 and result.get("code") == 0:
                user_data = result.get("data", {})
                info = {
                    "email": user_data.get("email", "未知"),
                    "package": "Free(升级)" if user_data.get("vip", 0) in [0, 10] else f"VIP{user_data.get('vip')}(付费)",
                    "left_days": user_data.get("leftDays", "0").split('.')[0],
                    "userId": str(user_data.get("userId", "未知")),
                    "code": user_data.get("code", "未知"),
                    "port": str(user_data.get("port", "未知"))
                }

                # 打印带emoji的个人信息
                print(f"{self.log_prefix()} 📧 账户邮箱: {info['email']}")
                print(f"{self.log_prefix()} 📦 套餐类型: {info['package']}")
                print(f"{self.log_prefix()} ⏳ 剩余天数: {info['left_days']} (充值)")

                # 生成Clash链接
                if info["userId"] != "未知" and info["code"] != "未知" and info["port"] != "未知":
                    clash_url = self.clash_url_template.format(**info)                    
                    print(f"{self.log_prefix()}  🔗 Clash订阅链接: {clash_url}")
                else:
                    print(f"\n{self.log_prefix()} ⚠️ 无法生成订阅链接(userId/code/port不完整)")
                print()
                return True
            else:
                print(f"{self.log_prefix()} ❌ 个人信息获取失败:{result.get('message', '响应异常')}\n")
                return False
        except json.JSONDecodeError:
            print(f"{self.log_prefix()} ❌ 解析失败:响应不是合法JSON\n")
            return False
        except requests.exceptions.RequestException as e:
            print(f"{self.log_prefix()} ❌ 信息请求失败:{str(e)}\n")
            return False

    def auto_checkin(self):
        """单账号执行签到流程"""
        print(f"\n{self.log_prefix()} ============== 开始签到流程 ==============")
        if not self.get_user_info():
            print(f"{self.log_prefix()} ⚠️ 个人信息获取失败,跳过本次签到\n")
            return False

        try:
            print(f"{self.log_prefix()} 🚀 发起签到请求...")
            checkin_data = json.dumps({"token": "glados.one"})
            response = self.session.post(self.checkin_url, data=checkin_data, timeout=15)
            response.encoding = "utf-8"
            result = response.json()

            if response.status_code == 200:
                code = result.get("code")
                message = result.get("message", "未知")
                points = result.get("points", 0)
                balance = result.get("list", [{}])[0].get("balance", "未知")

                if code == 1 and "Repeats" in message:
                    print(f"{self.log_prefix()} ⚠️ 签到结果:{message}")
                    print(f"{self.log_prefix()} 💰 当前积分:{balance}\n")
                elif code == 0 or "Success" in message:
                    print(f"{self.log_prefix()} ✅ 签到成功!")
                    print(f"{self.log_prefix()} 🎁 本次获积分:{points}")
                    print(f"{self.log_prefix()} 💰 当前积分:{balance}\n")
                else:
                    print(f"{self.log_prefix()} ❌ 签到失败:{message}(code={code})\n")
                return code in [0, 1]  # 成功/重复都算“流程完成”,其他算失败
            else:
                print(f"{self.log_prefix()} ❌ 签到接口异常,状态码:{response.status_code}\n")
                return False
        except json.JSONDecodeError:
            print(f"{self.log_prefix()} ❌ 解析签到响应失败:非合法JSON\n")
            return False
        except requests.exceptions.RequestException as e:
            print(f"{self.log_prefix()} ❌ 签到请求失败:{str(e)}\n")
            return False

def parse_cookies(cookie_str):
    """将Cookie字符串(格式:key1=val1; key2=val2)拆分为字典"""
    cookies_dict = {}
    for item in cookie_str.strip().split(';'):
        if '=' in item:
            key, val = item.strip().split('=', 1)  # 只按第一个=拆分(避免val含=)
            cookies_dict[key] = val
    return cookies_dict

def main():
    """主函数:读取环境变量、拆分多账号、逐个执行"""
    # 从青龙环境变量获取多账号配置
    glados_ck = os.getenv("GLaDOS_CK")
    if not glados_ck:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 未找到环境变量 GLaDOS_CK,请先配置")
        return

    # 按回车拆分多账号(青龙中多行环境变量会自动按\n分隔)
    accounts = [acc.strip() for acc in glados_ck.split('\n') if acc.strip()]
    if not accounts:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 环境变量 GLaDOS_CK 为空,请检查配置")
        return

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📢 共检测到 {len(accounts)} 个GLaDOS账号,开始批量处理...\n")

    # 逐个账号执行签到
    for idx, account in enumerate(accounts, 1):
        # 拆分单账号的Cookie和Authorization(格式:Cookie#Authorization)
        if '#' not in account:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [账号{idx}] ❌ 格式错误(需为Cookie#Authorization),跳过该账号\n")
            continue
        cookie_str, authorization = account.split('#', 1)
        cookies_dict = parse_cookies(cookie_str)

        # 执行单账号签到
        checker = GLaDOSAutoCheckin(cookies_dict, authorization, idx)
        checker.auto_checkin()

        # 账号间延迟(避免请求过快被拦截)
        if idx < len(accounts):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏳ 等待5秒后处理下一个账号...\n")
            time.sleep(5)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📢 所有账号处理完成!")

if __name__ == "__main__":
    main()
