# cloud-functions/api/photo/index.py
# 路由: /api/photo 及其子路径
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.client import JmClient


class handler(BaseHTTPRequestHandler):
    """处理 /api/photo 下的所有请求"""
    
    jm_client = JmClient()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        path_parts = [p for p in path.split('/') if p]
        
        photo_id = None
        if len(path_parts) >= 3:
            photo_id = path_parts[2]
        
        if not photo_id:
            params = parse_qs(parsed.query)
            photo_id = params.get('id', [None])[0]
        
        if not photo_id:
            self._send_json(200, {
                'message': '请使用 /api/photo/<photo_id> 或 /api/photo?id=<photo_id>',
                'example': '/api/photo/1220752'
            })
            return
        
        self._get_photo(photo_id)
    
    def _get_photo(self, photo_id):
        try:
            raw_data = self.jm_client.get('/chapter', params={'id': photo_id})
            
            images = raw_data.get('images', [])
            
            if not images:
                self._send_json(200, {
                    'code': 200,
                    'data': {
                        'photo_id': photo_id,
                        'title': '',
                        'image_count': 0,
                        'images': []
                    }
                })
                return
            
            image_list = []
            for idx, img_name in enumerate(images, 1):
                image_list.append({
                    'index': idx,
                    'filename': img_name,
                    'url': f'https://cdn-msp.jmapiproxy1.cc/media/photos/{photo_id}/{img_name}'
                })
            
            # ★ 从 raw_data 中提取标题，确保中文正常
            title = raw_data.get('name', '')
            
            self._send_json(200, {
                'code': 200,
                'data': {
                    'photo_id': photo_id,
                    'title': title,
                    'image_count': len(image_list),
                    'images': image_list
                }
            })
        except Exception as e:
            self._send_error(500, str(e))
    
    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        # ★ 确保 ensure_ascii=False，保留中文
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _send_error(self, status, msg):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({
            'code': status,
            'error': msg
        }, ensure_ascii=False).encode('utf-8'))