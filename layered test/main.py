# main.py 示例组合
from collector import tail_file
from parser import parse_line
from storage import store_event
from analyzer import analyze_event
from alerter import send_email_alert  # 或其他动作

def process_line(raw): # 处理每一行日志
    event = parse_line(raw)
    if event:
        store_event(event)
        alert = analyze_event(event)
        if alert and alert.get("alert"):
            send_email_alert(alert)

tail_file("/var/log/auth.log", process_line) # 监控日志文件并处理新行