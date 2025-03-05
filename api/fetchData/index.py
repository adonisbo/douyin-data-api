import os
from http.server import BaseHTTPRequestHandler
import json
from requests_html import HTMLSession

def get_douyin_data(user_id):
    session = HTMLSession()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Cookie": os.environ.get("DOUYIN_COOKIE", "")  # 从环境变量读取
    }
    
    try:
        # 新版抖音页面结构适配（2024年7月）
        resp = session.get(f"https://www.douyin.com/user/{user_id}", headers=headers, timeout=10)
        resp.html.render(timeout=20)
        
        # 数据定位策略
        stats = resp.html.find('div[data-e2e="user-info-container"] span.yn00wqwo')
        if len(stats) >= 3:
            return {
                "fans": stats[0].text,
                "follows": stats[1].text,
                "likes": stats[2].text
            }
        else:
            return {"error": "数据解析失败，请检查页面结构"}
    except Exception as e:
        return {"error": str(e)}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # 解决CORS问题
        self.end_headers()
        
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length))
        user_id = post_data.get("user_id", "")
        
        result = get_douyin_data(user_id)
        self.wfile.write(json.dumps(result).encode())
