# cloud-functions/api/utils/client.py
import json
import time
import random
import re
import logging
from typing import Optional, Dict, List
import requests
import threading

logger = logging.getLogger(__name__)


class Config:
    """配置类 - 所有配置硬编码"""
    
    # 域名服务器
    DOMAIN_SERVERS = [
        'https://rup4a04-c01.tos-ap-southeast-1.bytepluses.com/newsvr-2025.txt',
        'https://rup4a04-c02.tos-cn-hongkong.bytepluses.com/newsvr-2025.txt',
    ]
    
    # 降级域名（硬编码）
    FALLBACK_DOMAINS = [
        'www.cdnaspa.club',
        'www.cdnaspa.vip',
        'www.cdnplaystation6.cc',
        'www.cdnjmcomic.com',
        'www.jmcomic1.com',
        'www.jmcomic2.com',
        'www.jmcomic3.com',
    ]
    
    # 重试配置
    RETRY_TIMES = 3
    TIMEOUT = 30
    RETRY_DELAY_BASE = 1  # 基础延迟（秒）
    RETRY_MAX_DELAY = 10  # 最大延迟（秒）
    
    # 可重试的 HTTP 状态码
    RETRYABLE_STATUS = [429, 500, 502, 503, 504]
    
    # 完整请求头
    HEADERS = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
        'X-Requested-With': 'com.JMComic3.app',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }
    
    # IP 池（用于 X-Forwarded-For）
    IP_POOL = [
        '192.168.1.{}'.format(i) for i in range(1, 255)
    ] + [
        '10.0.0.{}'.format(i) for i in range(1, 255)
    ]


class JmClient:
    """禁漫API客户端 - 完整修复版"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(Config.HEADERS)
        self.cookies = {}
        self._domains = None
        self._domain_lock = threading.Lock()
        self._domain_index = 0
        self._last_domain_fetch = 0
        self._domain_cache_ttl = 3600  # 1小时缓存
        
        # 禁用 SSL 警告（生产环境应启用验证）
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _get_domains(self) -> list:
        """获取域名列表 - 增强版"""
        current_time = time.time()
        
        # 检查缓存是否有效
        if self._domains is not None:
            if current_time - self._last_domain_fetch < self._domain_cache_ttl:
                return self._domains
        
        # 尝试从服务器获取
        for server_url in Config.DOMAIN_SERVERS:
            try:
                response = self.session.get(
                    server_url, 
                    timeout=10, 
                    verify=False,
                    headers={'User-Agent': Config.HEADERS['User-Agent']}
                )
                
                if response.status_code == 200:
                    from .crypto import JmCrypto
                    decrypted = JmCrypto.decrypt_domain_data(response.text)
                    
                    if decrypted and len(decrypted) > 0:
                        with self._domain_lock:
                            self._domains = decrypted
                            self._last_domain_fetch = current_time
                        logger.info(f"获取域名成功: {len(decrypted)} 个域名")
                        return self._domains
                        
            except requests.Timeout:
                logger.warning(f"域名服务器超时: {server_url}")
                continue
            except Exception as e:
                logger.warning(f"获取域名失败: {server_url}, 错误: {e}")
                continue
        
        # 使用降级域名
        logger.warning("使用降级域名列表")
        with self._domain_lock:
            self._domains = Config.FALLBACK_DOMAINS
            self._last_domain_fetch = current_time
        return self._domains
    
    def _validate_domain(self, domain: str) -> bool:
        """验证域名是否可用"""
        try:
            test_url = f'https://{domain}/'
            response = self.session.get(
                test_url, 
                timeout=5, 
                verify=False,
                headers={'User-Agent': Config.HEADERS['User-Agent']}
            )
            return response.status_code < 500
        except:
            return False
    
    def _get_random_ip(self) -> str:
        """获取随机 IP"""
        return random.choice(Config.IP_POOL)
    
    def _build_url(self, path: str) -> str:
        """构建请求 URL - 线程安全"""
        domains = self._get_domains()
        
        # 尝试多个域名
        max_attempts = min(len(domains), 5)
        for attempt in range(max_attempts):
            with self._domain_lock:
                domain = domains[self._domain_index % len(domains)]
                self._domain_index += 1
            
            # 验证域名（每隔一段时间验证）
            if attempt > 0 or self._domain_index % 10 == 0:
                if not self._validate_domain(domain):
                    logger.warning(f"域名不可用: {domain}")
                    continue
            
            return f'https://{domain}{path}'
        
        # 如果所有域名都不可用，使用最后一个
        return f'https://{domains[0]}{path}'
    
    def _build_headers(self, path: str, domain: str) -> tuple:
        """构建完整的请求头"""
        from .crypto import JmCrypto
        
        timestamp = str(int(time.time()))
        token, token_param = JmCrypto.generate_token(timestamp)
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
            'X-Requested-With': 'com.JMComic3.app',
            'token': token,
            'tokenparam': token_param,
            'Origin': f'https://{domain}',
            'Referer': f'https://{domain}/',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'X-Forwarded-For': self._get_random_ip(),
        }
        
        return headers, timestamp
    
    def _is_retryable(self, error: Exception) -> bool:
        """判断错误是否可重试"""
        if isinstance(error, requests.Timeout):
            return True
        if isinstance(error, requests.ConnectionError):
            return True
        
        if hasattr(error, 'response') and hasattr(error.response, 'status_code'):
            return error.response.status_code in Config.RETRYABLE_STATUS
        
        return False
    
    def _request(self, method: str, path: str, params: Optional[Dict] = None,
                 data: Optional[Dict] = None, retry: int = 0) -> Dict:
        """核心请求方法 - 增强版"""
        if retry >= Config.RETRY_TIMES:
            raise Exception(f"请求失败，已重试{retry}次: {path}")
        
        try:
            # 构建请求
            domains = self._get_domains()
            domain = random.choice(domains)
            url = f'https://{domain}{path}'
            headers, timestamp = self._build_headers(path, domain)
            
            # 更新 Cookie
            if self.cookies:
                self.session.cookies.update(self.cookies)
            
            logger.info(f"请求: {method} {url}")
            logger.debug(f"Headers: token={headers.get('token', '')[:10]}...")
            
            # 发送请求
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
            
            logger.info(f"响应状态: {response.status_code}")
            
            # 处理不同的 HTTP 状态码
            if response.status_code == 200:
                # 正常响应
                pass
            elif response.status_code == 401:
                # Token 过期，清除 Cookie 重试
                logger.warning("Token 过期，清除 Cookie 重试")
                self.session.cookies.clear()
                self.cookies.clear()
                return self._request(method, path, params, data, retry + 1)
            elif response.status_code == 429:
                # 限流，等待后重试
                wait_time = min(Config.RETRY_DELAY_BASE * (2 ** retry) + random.uniform(0, 1), Config.RETRY_MAX_DELAY)
                logger.warning(f"请求限流，等待 {wait_time:.2f}s 后重试")
                time.sleep(wait_time)
                return self._request(method, path, params, data, retry + 1)
            elif response.status_code >= 500:
                # 服务器错误，切换域名重试
                logger.warning(f"服务器错误 {response.status_code}，切换域名重试")
                with self._domain_lock:
                    self._domain_index += 1
                wait_time = min(Config.RETRY_DELAY_BASE * (2 ** retry), Config.RETRY_MAX_DELAY)
                time.sleep(wait_time)
                return self._request(method, path, params, data, retry + 1)
            else:
                # 其他错误
                raise Exception(f"HTTP {response.status_code}")
            
            # 检查响应内容
            response_text = response.text.strip()
            if not response_text:
                raise Exception("响应为空")
            
            # 检查是否为 JSON
            if not response_text.startswith('{') and not response_text.startswith('['):
                # 尝试修复：可能包含前导字符
                json_start = response_text.find('{')
                if json_start != -1:
                    response_text = response_text[json_start:]
                else:
                    raise Exception(f"非JSON响应: {response_text[:100]}")
            
            # 解析 JSON
            try:
                result = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析失败: {e}")
                logger.debug(f"响应内容: {response_text[:200]}")
                raise Exception(f"JSON 解析失败: {e}")
            
            # 检查 API 状态码
            if result.get('code') != 200:
                error_msg = result.get('msg', '未知错误')
                logger.warning(f"API 错误: {error_msg}")
                raise Exception(f"API错误: {error_msg}")
            
            # 解密数据
            encrypted_data = result.get('data')
            if encrypted_data:
                try:
                    from .crypto import JmCrypto
                    decrypted = JmCrypto.decrypt_api_data(encrypted_data, timestamp)
                    return json.loads(decrypted)
                except Exception as e:
                    logger.error(f"解密失败: {e}")
                    raise Exception(f"数据解密失败: {e}")
            
            return result
            
        except requests.Timeout as e:
            logger.warning(f"请求超时 (尝试 {retry+1}/{Config.RETRY_TIMES}): {e}")
            wait_time = min(Config.RETRY_DELAY_BASE * (2 ** retry), Config.RETRY_MAX_DELAY)
            time.sleep(wait_time)
            return self._request(method, path, params, data, retry + 1)
            
        except requests.ConnectionError as e:
            logger.warning(f"连接错误 (尝试 {retry+1}/{Config.RETRY_TIMES}): {e}")
            # 切换域名
            with self._domain_lock:
                self._domain_index += 1
            wait_time = min(Config.RETRY_DELAY_BASE * (2 ** retry), Config.RETRY_MAX_DELAY)
            time.sleep(wait_time)
            return self._request(method, path, params, data, retry + 1)
            
        except Exception as e:
            if self._is_retryable(e):
                logger.warning(f"请求失败 (尝试 {retry+1}/{Config.RETRY_TIMES}): {e}")
                wait_time = min(Config.RETRY_DELAY_BASE * (2 ** retry), Config.RETRY_MAX_DELAY)
                time.sleep(wait_time)
                return self._request(method, path, params, data, retry + 1)
            else:
                logger.error(f"不可重试的错误: {e}")
                raise
    
    def get(self, path: str, params: Optional[Dict] = None) -> Dict:
        """GET 请求"""
        return self._request('GET', path, params)
    
    def post(self, path: str, data: Optional[Dict] = None) -> Dict:
        """POST 请求"""
        return self._request('POST', path, data=data)
    
    def get_album(self, album_id: str) -> Dict:
        """获取本子详情"""
        return self.get('/album', params={'id': album_id})
    
    def get_photo(self, photo_id: str) -> Dict:
        """获取章节详情"""
        return self.get('/chapter', params={'id': photo_id})