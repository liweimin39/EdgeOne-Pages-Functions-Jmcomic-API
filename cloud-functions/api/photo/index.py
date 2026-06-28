# cloud-functions/api/photo/index.py
# 路由: /api/photo 及其子路径
from http.server import BaseHTTPRequestHandler
import json
import logging
from urllib.parse import urlparse, parse_qs
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.client import JmClient
from utils.parser import JmParser

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    """处理 /api/photo 下的所有请求"""
    
    jm_client = JmClient()
    
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path.rstrip('/')
            
            # 1. 首先尝试从查询参数获取 photo_id
            params = parse_qs(parsed.query)
            photo_id = params.get('id', [None])[0]
            
            # 2. 如果查询参数没有，尝试从路径提取
            if not photo_id:
                if path.startswith('/api'):
                    path = path[4:]
                
                path_parts = [p for p in path.split('/') if p]
                
                if len(path_parts) >= 2:
                    photo_id = path_parts[1]
                elif len(path_parts) == 1:
                    photo_id = path_parts[0]
            
            # 如果没有 photo_id，显示用法
            if not photo_id:
                self._send_json(200, {
                    'message': '请使用 /api/photo/<photo_id> 或 /api/photo?id=<photo_id>',
                    'example': '/api/photo/{photo_id}',
                    'example_query': '/api/photo?id={photo_id}',
                    'note': 'photo_id 是章节 ID，可以从 /api/album 接口获取'
                })
                return
            
            if not photo_id.isdigit():
                self._send_error(400, 'photo_id 必须是纯数字')
                return
            
            self._get_photo(photo_id)
            
        except Exception as e:
            logger.error(f"请求处理异常: {e}", exc_info=True)
            self._send_error(500, '服务器内部错误，请稍后重试')
    
    def _get_photo(self, photo_id):
        """获取章节图片列表"""
        try:
            logger.info(f"获取章节数据: {photo_id}")
            
            raw_data = self.jm_client.get_photo(photo_id)
            
            if not raw_data:
                self._send_error(404, f'章节 {photo_id} 不存在或数据为空')
                return
            
            # 使用 Parser 解析数据
            photo_data = JmParser.parse_photo(raw_data, photo_id)
            
            self._send_json(200, {
                'code': 200,
                'data': photo_data
            })
            
            logger.info(f"章节数据获取成功: {photo_id}, 图片数: {photo_data.get('image_count', 0)}")
            
        except Exception as e:
            logger.error(f"获取章节数据失败: {photo_id}, 错误: {e}", exc_info=True)
            
            error_msg = str(e).lower()
            if '404' in error_msg or '不存在' in error_msg or 'not found' in error_msg:
                self._send_error(404, f'章节 {photo_id} 不存在')
            elif '超时' in error_msg or 'timeout' in error_msg:
                self._send_error(504, '请求超时，请稍后重试')
            elif '限流' in error_msg or '429' in error_msg or 'too many' in error_msg:
                self._send_error(429, '请求过于频繁，请稍后重试')
            else:
                self._send_error(500, f'获取数据失败: {str(e)}')
    
    def _send_json(self, status, data):
        try:
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.end_headers()
            
            response_json = json.dumps(data, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))
        except Exception as e:
            logger.error(f"发送响应失败: {e}")
    
    def _send_error(self, status, msg):
        try:
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_data = {
                'code': status,
                'error': msg
            }
            response_json = json.dumps(error_data, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))
        except Exception as e:
            logger.error(f"发送错误响应失败: {e}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()