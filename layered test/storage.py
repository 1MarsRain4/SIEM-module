# storage.py
import sqlite3
import json

from parser import parse_line  # 从 parser 模块导入解析函数
from datetime import datetime

DB_PATH = "siem_events.db"

def init_db(): # 初始化数据库，创建事件表
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        event_type TEXT,
        src_ip TEXT,
        user TEXT,
        severity TEXT,
        raw TEXT,
        json_data TEXT
    )
    """)
    conn.commit()
    return conn

def store_event(event: dict): # 存储事件到数据库
    conn = sqlite3.connect(DB_PATH) # 连接数据库
    conn.execute("""
    INSERT INTO events (timestamp, event_type, src_ip, user, severity, raw, json_data) 
    VALUES (?, ?, ?, ?, ?, ?, ?) # 使用参数化查询防止 SQL 注入
    """, ( 
        event["timestamp"],
        event.get("event_type"),
        event.get("src_ip"),
        event.get("user"),
        event.get("severity"),
        event["raw"],
        json.dumps(event)
    )) # 将事件字典转换为 JSON 存储
    conn.commit()
    conn.close()

# 使用示例：结合 parser
if __name__ == "__main__":
    init_db()
    sample_event = parse_line("Failed password for test from 1.2.3.4 port 22 ssh2") # 从 parser 导入解析函数，解析示例日志行
    if sample_event:
        store_event(sample_event)