# cloud-functions/api/album/index.py
# 路由: /api/album 及其子路径
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.client import JmClient
from utils.parser import JmParser


class handler(BaseHTTPRequestHandler):
    """处理 /api/album 下的所有请求"""
    
    jm_client = JmClient()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        path_parts = [p for p in path.split('/') if p]
        
        # 尝试从路径提取 album_id
        album_id = None
        if len(path_parts) >= 3:
            album_id = path_parts[2]
        
        # 如果路径没有，尝试从查询参数获取
        if not album_id:
            params = parse_qs(parsed.query)
            album_id = params.get('id', [None])[0]
        
        # 如果没有 album_id，显示用法
        if not album_id:
            self._send_json(200, {
                'message': '请使用 /api/album/<album_id> 或 /api/album?id=<album_id>',
                'example': '/api/album/1220749',
                'example_query': '/api/album?id=1220749'
            })
            return
        
        # ★ 直接获取本子详情 + 章节列表，不再区分 /photos
        self._get_album_photos(album_id)
    
    def _get_album_photos(self, album_id):
        try:
            raw_data = self.jm_client.get_album(album_id)
            album = JmParser.parse_album(raw_data)
            
            photos = []
            for photo in album.photos:
                photos.append({
                    'photo_id': photo.photo_id,
                    'title': photo.title,
                    'sort': photo.sort,
                    'image_count': len(photo.images)
                })
            
            self._send_json(200, {
                'code': 200,
                'data': {
                    'album_id': album.album_id,
                    'album_title': album.title,
                    'author': album.author,
                    'authors': album.authors,
                    'tags': album.tags,
                    'cover_url': album.cover_url,
                    'views': album.views,
                    'likes': album.likes,
                    'total_photos': len(photos),
                    'photos': photos
                }
            })
        except Exception as e:
            self._send_error(500, str(e))
    
    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _send_error(self, status, msg):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({
            'code': status,
            'error': msg
        }, ensure_ascii=False).encode('utf-8'))