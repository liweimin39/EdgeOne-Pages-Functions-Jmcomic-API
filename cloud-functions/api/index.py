# cloud-functions/api/index.py
# 路由: /api - 服务信息
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class handler(BaseHTTPRequestHandler):
    """处理 /api 根路径请求"""
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        
        # 处理 /api 或 /api/ 路径
        if path == '' or path == '/' or path == '/api':
            self._send_service_info()
        else:
            self._send_not_found()
    
    def _send_service_info(self):
        """发送服务信息"""
        data = {
            'service': 'Jmcomic API',
            'version': '2.0.0',
            'description': '禁漫天堂数据 API 服务',
            'endpoints': {
                'album': {
                    'description': '获取本子详情',
                    'methods': ['GET'],
                    'usage': '/api/album/{album_id} 或 /api/album?id={album_id}'
                },
                'photo': {
                    'description': '获取章节图片列表',
                    'methods': ['GET'],
                    'usage': '/api/photo/{photo_id} 或 /api/photo?id={photo_id}'
                },
                'api': {
                    'description': '服务信息',
                    'methods': ['GET'],
                    'usage': '/api'
                }
            }
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def _send_not_found(self):
        """404 响应"""
        self.send_response(404)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'code': 404,
            'error': '接口不存在，请访问 /api 查看可用接口'
        }, ensure_ascii=False).encode('utf-8'))