import re
import time
import smtplib
from email.mime.text import MIMEText
from collections import defaultdict
from datetime import datetime, timedelta

# 配置参数
LOG_FILE = '/var/log/auth.log'  # 替换为实际日志路径（需读权限）
ALERT_THRESHOLD = 3  # 失败登录阈值
TIME_WINDOW = timedelta(minutes=1)  # 时间窗口
SMTP_SERVER = 'smtp.example.com'  # 替换为你的 SMTP 服务器
SMTP_PORT = 587 # 替换为你的 SMTP 端口
SENDER_EMAIL = 'alert@example.com' # 替换为你的发送邮箱
SENDER_PASSWORD = 'your_password' # 替换为你的发送邮箱密码
RECIPIENT_EMAIL = 'admin@example.com' # 替换为你的接收邮箱

# 正则表达式解析 sshd 登录日志（示例：Failed password for user from IP）
FAILED_LOGIN_PATTERN = re.compile(r'Failed password for (\w+) from ([\d.]+) port \d+ ssh2')
SUCCESS_LOGIN_PATTERN = re.compile(r'Accepted password for (\w+) from ([\d.]+) port \d+ ssh2')

class LoginTracker: # 追踪登录失败的类
    def __init__(self):
        self.failures = defaultdict(list)  # IP -> list of failure timestamps

    def process_log_line(self, line):
        failed_match = FAILED_LOGIN_PATTERN.search(line)
        if failed_match: # 如果匹配到失败登录
            user, ip = failed_match.groups()
            now = datetime.now() # 当前时间
            self.failures[ip].append(now) # 记录失败时间
            # 清理过期记录
            self.failures[ip] = [t for t in self.failures[ip] if now - t < TIME_WINDOW]
            # 检查阈值
            if len(self.failures[ip]) >= ALERT_THRESHOLD:
                self.send_alert(ip, user, len(self.failures[ip]))
                self.failures[ip] = []  # 重置计数以避免重复告警

        success_match = SUCCESS_LOGIN_PATTERN.search(line)
        if success_match:
            user, ip = success_match.groups()
            print(f"Successful login: User {user} from {ip}")

    def send_alert(self, ip, user, count):
        msg = MIMEText(f"Abnormal login detected: {count} failed attempts for user {user} from IP {ip}")
        msg['Subject'] = 'Security Alert: Abnormal Login'
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
            server.quit()
            print("Alert sent successfully")
        except Exception as e:
            print(f"Failed to send alert: {e}")

def tail_log_file(file_path):
    with open(file_path, 'r') as f:
        # 移动到文件末尾
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)  # 轮询间隔
                continue
            yield line.strip()

# 主函数
if __name__ == '__main__':
    tracker = LoginTracker()
    print("Starting log monitoring...")
    for line in tail_log_file(LOG_FILE):
        tracker.process_log_line(line)