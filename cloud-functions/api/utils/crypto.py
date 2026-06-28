# cloud-functions/api/utils/crypto.py
import base64
import hashlib
import json
import logging
from Crypto.Cipher import AES

logger = logging.getLogger(__name__)


class JmCrypto:
    """禁漫加密工具 - 增强版"""
    
    APP_TOKEN_SECRET = '185Hcomic3PAPP7R'
    APP_DATA_SECRET = '185Hcomic3PAPP7R'
    APP_VERSION = '2.0.26'
    API_DOMAIN_SECRET = 'diosfjckwpqpdfjkvnqQjsik'
    
    @classmethod
    def md5hex(cls, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @classmethod
    def generate_token(cls, timestamp: str) -> tuple:
        token_param = f'{timestamp},{cls.APP_VERSION}'
        token = cls.md5hex(f'{timestamp}{cls.APP_TOKEN_SECRET}')
        return token, token_param
    
    @classmethod
    def decrypt_api_data(cls, encrypted_data: str, timestamp: str, secret: str = None) -> str:
        """解密 API 数据 - 增强错误处理"""
        try:
            if secret is None:
                secret = cls.APP_DATA_SECRET
            
            # 清理输入数据
            encrypted_data = encrypted_data.strip()
            if not encrypted_data:
                raise ValueError("加密数据为空")
            
            # Base64 解码
            try:
                encrypted_bytes = base64.b64decode(encrypted_data)
            except Exception as e:
                raise ValueError(f"Base64 解码失败: {e}")
            
            # 生成密钥
            key = cls.md5hex(f'{timestamp}{secret}').encode('utf-8')
            
            # AES-ECB 解密
            try:
                cipher = AES.new(key, AES.MODE_ECB)
                decrypted = cipher.decrypt(encrypted_bytes)
            except Exception as e:
                raise ValueError(f"AES 解密失败: {e}")
            
            # 移除 PKCS7 填充
            try:
                padding_len = decrypted[-1]
                
                # 验证填充长度有效性
                if padding_len < 1 or padding_len > 16:
                    # 如果不是 PKCS7 填充，尝试直接解码
                    return decrypted.decode('utf-8')
                
                # 验证填充数据
                if not all(b == padding_len for b in decrypted[-padding_len:]):
                    # 填充无效，尝试直接解码
                    try:
                        return decrypted.decode('utf-8')
                    except:
                        raise ValueError("填充数据无效")
                
                result = decrypted[:-padding_len].decode('utf-8')
                return result
                
            except UnicodeDecodeError as e:
                # UTF-8 解码失败，尝试其他编码
                try:
                    return decrypted.decode('gbk')
                except:
                    raise ValueError(f"解码失败: {e}")
                    
        except Exception as e:
            logger.error(f"解密失败: {e}")
            raise Exception(f"解密失败: {e}")
    
    @classmethod
    def decrypt_domain_data(cls, encrypted_data: str) -> list:
        """解密域名列表 - 增强版"""
        try:
            # 清理数据
            text = encrypted_data.strip()
            
            # 移除前导非 ASCII 字符
            while text and not text[0].isascii():
                text = text[1:]
            
            if not text:
                return []
            
            # 尝试解密
            try:
                decrypted = cls.decrypt_api_data(text, '', cls.API_DOMAIN_SECRET)
            except Exception as e:
                logger.warning(f"域名解密失败: {e}")
                return []
            
            # 解析 JSON
            try:
                data = json.loads(decrypted)
                domains = data.get('Server', [])
                
                # 验证域名格式
                valid_domains = []
                for domain in domains:
                    if isinstance(domain, str) and domain.strip():
                        # 移除可能的协议前缀
                        domain = domain.strip().replace('https://', '').replace('http://', '')
                        if '.' in domain:  # 简单验证是否为域名
                            valid_domains.append(domain)
                
                return valid_domains
                
            except json.JSONDecodeError as e:
                logger.warning(f"域名 JSON 解析失败: {e}")
                return []
                
        except Exception as e:
            logger.error(f"域名解密异常: {e}")
            return []