# analyzer.py
from collections import defaultdict, deque 
from datetime import datetime, timedelta

class FailureWindow: # 监控短时间内的失败事件
    def __init__(self, threshold=5, window_sec=300): # threshold: 失败次数阈值, window_sec: 时间窗口长度（秒）
        self.failures = defaultdict(lambda: deque(maxlen=100)) # 存储每个IP的失败事件时间戳，使用deque自动丢弃过旧的记录
        self.threshold = threshold
        self.window = timedelta(seconds=window_sec) # 转换为timedelta对象，方便时间比较

    def add_failure(self, ip: str, ts: datetime): # 添加失败事件
        self.failures[ip].append(ts) # 添加当前失败事件的时间戳
        # 清理过期
        while self.failures[ip] and ts - self.failures[ip][0] > self.window: # 移除窗口外的旧记录
            self.failures[ip].popleft()

    def is_brute_force(self, ip: str) -> bool: # 判断是否达到暴力攻击的条件
        if len(self.failures[ip]) >= self.threshold: # 如果当前IP的失败事件数量超过阈值，认为可能是暴力攻击
            return True
        return False

# 规则示例：短时间多次失败登录
analyzer = FailureWindow(threshold=4, window_sec=120)

def analyze_event(event: dict): # 分析事件，判断是否触发暴力攻击规则
    if event.get("event_type") == "authentication_failure": 
        ts = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00")) # 解析时间戳，处理UTC格式
        ip = event["src_ip"]
        analyzer.add_failure(ip, ts)
        if analyzer.is_brute_force(ip):
            return {
                "alert": True,
                "type": "brute_force_attempt",
                "ip": ip,
                "count": len(analyzer.failures[ip]),
                "time_window": "2分钟"
            }
    return None