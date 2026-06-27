# cloud-functions/api/index.py
# 路由: /api
from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    """Handler 类模式 - 路由: /api"""
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        
        self.wfile.write(json.dumps({
            'code': 200,
            'service': 'Jmcomic API',
            'version': '1.0',
            'routes': {
                '/api': '服务信息',
                '/api/album/<id>': '获取本子详情（包含章节列表）',
                '/api/album?id=<id>': '获取本子详情（包含章节列表）',
                '/api/photo/<id>': '获取章节图片列表',
                '/api/photo?id=<id>': '获取章节图片列表',
            },
            'example': {
                '本子详情': '/api/album/1220749',
                '章节图片': '/api/photo/1220752',
            }
        }, ensure_ascii=False).encode('utf-8'))