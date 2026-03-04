# dashboard.py - 极简 Web 展示
from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

HTML = """
<!doctype html>
<title>SIEM Mini Dashboard</title>
<h1>最近告警事件</h1>
<table border=1>
<tr><th>时间</th><th>类型</th><th>IP</th><th>用户</th><th>原始日志</th></tr>
{% for row in events %}
<tr><td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td><td>{{ row[6][:100] }}</td></tr>
{% endfor %}
</table>
"""

@app.route("/") # 首页显示最近的告警事件
def dashboard(): # 从数据库读取最近的事件并展示
    conn = sqlite3.connect("siem_events.db")
    cur = conn.cursor() # 查询最近的事件
    cur.execute("SELECT timestamp, event_type, src_ip, user, severity, raw FROM events ORDER BY timestamp DESC LIMIT 20")
    events = cur.fetchall() # 关闭数据库连接
    conn.close()
    return render_template_string(HTML, events=events) # 渲染 HTML 模板并返回

if __name__ == "__main__": # 启动 Flask 应用
    app.run(debug=True, port=5005)