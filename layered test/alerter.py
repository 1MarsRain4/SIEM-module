#alerter.py
import smtplib
from email.mime.text import MIMEText
import subprocess

def send_email_alert(alert_data: dict, to_email="admin@example.com"): # 发送告警邮件
    msg = MIMEText(f"高危告警：{alert_data}")
    msg['Subject'] = f"SIEM Alert - {alert_data.get('type', '未知')}"
    msg['From'] = "siem@example.com"
    msg['To'] = to_email

    with smtplib.SMTP("smtp.example.com", 587) as server: # 连接SMTP服务器
        server.starttls()
        server.login("siem@example.com", "password")
        server.send_message(msg)

def auto_block_ip(ip: str): # 自动封禁IP地址
    try: 
        # 注意：生产环境需谨慎，最好用 nftables 或专用防火墙接口
        subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True, timeout=10) # 使用iptables封禁IP，设置超时避免挂起
        print(f"已自动封禁 IP: {ip}")
    except Exception as e:
        print(f"封禁失败: {e}")

# 使用示例
if __name__ == "__main__": # 模拟接收到一个高危告警
    sample_alert = {"type": "brute_force_attempt", "ip": "1.2.3.4", "count": 7} # 模拟一个暴力攻击告警
    send_email_alert(sample_alert) # 发送告警邮件
    auto_block_ip(sample_alert["ip"]) # 自动封禁攻击IP