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
    print("  青龙日志工具（绝恋提供）  ")
    print("="*60)
    current_script_name = os.path.splitext(os.path.basename(__file__))[0]
    result = read_latest_ql_log(task_name_prefix=current_script_name, script_name=current_script_name)
    print(f"\n{result}")
    print("\n" + "="*60)
