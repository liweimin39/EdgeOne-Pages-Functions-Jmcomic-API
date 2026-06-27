# cloud-functions/api/utils/crypto.py
import base64
import hashlib
import json
from Crypto.Cipher import AES


class JmCrypto:
    """禁漫加密工具"""
    
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
        """解密 API 数据"""
        try:
            if secret is None:
                secret = cls.APP_DATA_SECRET
            
            encrypted_bytes = base64.b64decode(encrypted_data)
            key = cls.md5hex(f'{timestamp}{secret}').encode('utf-8')
            cipher = AES.new(key, AES.MODE_ECB)
            decrypted = cipher.decrypt(encrypted_bytes)
            padding_len = decrypted[-1]
            return decrypted[:-padding_len].decode('utf-8')
        except Exception as e:
            raise Exception(f"解密失败: {e}")
    
    @classmethod
    def decrypt_domain_data(cls, encrypted_data: str) -> list:
        """解密域名列表"""
        try:
            text = encrypted_data
            while text and not text[0].isascii():
                text = text[1:]
            
            decrypted = cls.decrypt_api_data(text, '', cls.API_DOMAIN_SECRET)
            data = json.loads(decrypted)
            return data.get('Server', [])
        except Exception as e:
            print(f"域名解密失败: {e}")
            return []