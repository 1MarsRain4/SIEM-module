# collector.py - 采集层示例
import socket
import threading
from pathlib import Path
import time

def tail_file(log_path: str, callback): # 定义一个函数来模拟 tail -f 功能，实时读取日志文件并调用回调函数处理新行
    """模拟 tail -f"""
    path = Path(log_path)
    last_size = path.stat().st_size # 获取文件初始大小，以便后续读取新增内容
    while True:
        time.sleep(0.2)
        current_size = path.stat().st_size # 获取当前文件大小，如果有新增内容，则读取新增部分并调用回调函数处理
        if current_size > last_size: # 如果文件有新增内容，则读取新增部分并调用回调函数处理
            with open(path, 'r') as f:
                f.seek(last_size) # 移动文件指针到上次读取的位置
                new_lines = f.readlines()
                for line in new_lines: # 处理每一行新增日志，调用回调函数
                    callback(line.strip()) # 去除行末的换行符并调用回调函数
            last_size = current_size

def start_syslog_udp_server(port=514, callback=None): # 定义一个函数来启动一个简单的 UDP Syslog 服务器，监听指定端口并调用回调函数处理接收到的日志消息
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 创建一个 UDP 套接字
    sock.bind(('0.0.0.0', port))
    print(f"Syslog UDP listening on :{port}")
    while True:
        data, addr = sock.recvfrom(4096) # 接收 UDP 消息
        line = data.decode('utf-8', errors='ignore').strip() # 解码消息并去除行末的换行符
        if callback:
            callback(line) # 调用回调函数处理接收到的日志消息

# 使用示例
if __name__ == "__main__": # 定义一个简单的回调函数来打印采集到的日志行
    def print_line(line):
        print(f"[采集] {line}") 

    # 启动文件 tail
    threading.Thread(target=tail_file, args=("/var/log/auth.log", print_line), daemon=True).start()

    # 启动 UDP Syslog 接收（可选）
    # threading.Thread(target=start_syslog_udp_server, args=(514, print_line), daemon=True).start()

    while True:
        time.sleep(10) # 主线程保持运行，采集线程在后台工作 # 可以根据需要添加更多的采集方式，如 TCP Syslog、API 采集等