# parser.py
import re
import json
from datetime import datetime

# 示例：sshd 失败登录正则
FAIL_PATTERN = re.compile(r'Failed password for (\S+) from ([\d.]+) port \d+ ssh2')

def parse_line(raw_line: str) -> dict | None: # 解析日志行，提取事件信息
    ts = datetime.utcnow().isoformat() + "Z"  # 实际应从日志提取时间
    event = {
        "timestamp": ts,
        "raw": raw_line,
        "source": "auth.log",
        "event_type": "unknown"
    }

    m = FAIL_PATTERN.search(raw_line) # 匹配失败登录事件
    if m:
        user, src_ip = m.groups()
        event.update({
            "event_type": "authentication_failure",
            "user": user,
            "src_ip": src_ip,
            "severity": "medium",
            "category": "authentication"
        })
        return event

    # 可继续添加成功登录、sudo、cron 等多种模式...
    return None  # 忽略不关心的日志

# 使用示例
if __name__ == "__main__": # 测试解析功能
    test_lines = [
        'Sep  4 10:15:23 server sshd[1234]: Failed password for invalid user admin from 192.168.1.100 port 12345 ssh2',
        'Sep  4 10:16:01 server sshd[5678]: Accepted password for rain from 203.0.113.50 port 54321 ssh2'
    ]
    for line in test_lines:
        parsed = parse_line(line) # 解析日志行,输出结果
        if parsed:
            print(json.dumps(parsed, indent=2, ensure_ascii=False))