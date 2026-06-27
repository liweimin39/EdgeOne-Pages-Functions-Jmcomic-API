# cloud-functions/api/utils/client.py
import json
import time
import random
import re
from typing import Optional, Dict
import requests


class Config:
    """配置类"""
    
    DOMAIN_SERVERS = [
        'https://rup4a04-c01.tos-ap-southeast-1.bytepluses.com/newsvr-2025.txt',
        'https://rup4a04-c02.tos-cn-hongkong.bytepluses.com/newsvr-2025.txt',
    ]
    
    RETRY_TIMES = 3
    TIMEOUT = 30
    
    # 完整的 API 请求头 - 模拟真实 APP
    HEADERS = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
        'X-Requested-With': 'com.JMComic3.app',
    }


class JmClient:
    """禁漫API客户端 - 完善版"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(Config.HEADERS)
        self.cookies = {}
        self._domains = None
        self._current_domain_index = 0
        
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _get_domains(self) -> list:
        if self._domains is not None:
            return self._domains
        
        for server_url in Config.DOMAIN_SERVERS:
            try:
                response = self.session.get(server_url, timeout=10, verify=False)
                if response.status_code == 200:
                    from .crypto import JmCrypto
                    decrypted = JmCrypto.decrypt_domain_data(response.text)
                    if decrypted:
                        self._domains = decrypted
                        return self._domains
            except Exception as e:
                print(f"获取域名失败: {e}")
                continue
        
        self._domains = [
            'www.cdnaspa.club',
            'www.cdnaspa.vip',
            'www.cdnplaystation6.cc',
        ]
        return self._domains
    
    def _build_url(self, path: str) -> str:
        domains = self._get_domains()
        domain = domains[self._current_domain_index % len(domains)]
        self._current_domain_index += 1
        return f'https://{domain}{path}'
    
    def _build_headers(self, path: str, domain: str) -> tuple:
        """构建完整的请求头"""
        from .crypto import JmCrypto
        
        timestamp = str(int(time.time()))
        token, token_param = JmCrypto.generate_token(timestamp)
        
        headers = {
            # 基础头
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
            'X-Requested-With': 'com.JMComic3.app',
            # 认证头
            'token': token,
            'tokenparam': token_param,
            # 来源头 - 关键
            'Origin': f'https://{domain}',
            'Referer': f'https://{domain}/',
        }
        
        return headers, timestamp
    
    def _request(self, method: str, path: str, params: Optional[Dict] = None,
                 data: Optional[Dict] = None, retry: int = 0) -> Dict:
        if retry >= Config.RETRY_TIMES:
            raise Exception(f"请求失败，已重试{retry}次: {path}")
        
        try:
            domains = self._get_domains()
            domain = random.choice(domains)
            url = f'https://{domain}{path}'
            headers, timestamp = self._build_headers(path, domain)
            
            if self.cookies:
                self.session.cookies.update(self.cookies)
            
            print(f"请求: {method} {url}")
            print(f"Headers: token={headers.get('token', '')[:10]}...")
            
            if method.upper() == 'GET':
                response = self.session.get(
                    url, 
                    params=params, 
                    headers=headers,
                    timeout=Config.TIMEOUT,
                    verify=False
                )
            else:
                response = self.session.post(
                    url, 
                    params=params, 
                    data=data,
                    headers=headers, 
                    timeout=Config.TIMEOUT,
                    verify=False
                )
            
            print(f"响应状态: {response.status_code}")
            print(f"响应内容前200字符: {response.text[:200]}")
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")
            
            # 检查是否是 JSON
            if not response.text.strip().startswith('{'):
                raise Exception(f"非JSON响应: {response.text[:100]}")
            
            result = response.json()
            
            if result.get('code') != 200:
                raise Exception(f"API错误: {result.get('msg', '未知错误')}")
            
            encrypted_data = result.get('data')
            if encrypted_data:
                from .crypto import JmCrypto
                decrypted = JmCrypto.decrypt_api_data(encrypted_data, timestamp)
                return json.loads(decrypted)
            
            return result
            
        except Exception as e:
            print(f"请求失败 (尝试 {retry+1}/{Config.RETRY_TIMES}): {e}")
            time.sleep(1)
            return self._request(method, path, params, data, retry + 1)
    
    def get(self, path: str, params: Optional[Dict] = None) -> Dict:
        return self._request('GET', path, params)
    
    def post(self, path: str, data: Optional[Dict] = None) -> Dict:
        return self._request('POST', path, data=data)
    
    def get_album(self, album_id: str) -> Dict:
        return self.get('/album', params={'id': album_id})
    
    def get_photo(self, photo_id: str) -> Dict:
        return self.get('/chapter', params={'id': photo_id})