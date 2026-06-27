# cloud-functions/api/utils/parser.py
import random
from typing import Dict, List
from .models import JmAlbum, JmPhoto, JmImage


class JmParser:
    """禁漫数据解析器"""
    
    CDN_DOMAINS = [
        'cdn-msp.jmapiproxy1.cc',
        'cdn-msp.jmapiproxy2.cc',
        'cdn-msp3.jmapiproxy2.cc',
    ]
    
    @classmethod
    def _decode_chinese(cls, text: str) -> str:
        """
        将禁漫 API 返回的乱码正确解码为中文
        禁漫 API 返回的是 GBK 编码的字节，但被当作 UTF-8 字符串读取了
        """
        if not text:
            return text
        try:
            # ★ 关键修复：将字符串先编码为 latin1（保留原始字节），再用 gbk 解码
            return text.encode('latin1').decode('gbk')
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                # 如果 gbk 失败，尝试 gb2312
                return text.encode('latin1').decode('gb2312')
            except (UnicodeEncodeError, UnicodeDecodeError):
                try:
                    # 如果上面都失败，尝试 utf-8
                    return text.encode('latin1').decode('utf-8')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    return text
    
    @classmethod
    def parse_album(cls, data: Dict) -> JmAlbum:
        """解析本子数据"""
        album_id = str(data.get('id', ''))
        title = cls._decode_chinese(data.get('name', ''))
        description = cls._decode_chinese(data.get('description', ''))
        
        authors = data.get('author', [])
        if isinstance(authors, str):
            authors = [cls._decode_chinese(authors)]
        else:
            authors = [cls._decode_chinese(a) for a in authors]
        author = authors[0] if authors else '未知'
        
        tags = data.get('tags', [])
        if isinstance(tags, str):
            tags = [cls._decode_chinese(t) for t in tags.split()]
        else:
            tags = [cls._decode_chinese(t) for t in tags]
        
        photos = []
        series = data.get('series', [])
        
        if series:
            for chapter in series:
                photo_id = str(chapter.get('id', ''))
                photo_title = cls._decode_chinese(chapter.get('name', ''))
                sort = chapter.get('sort', '1')
                
                images = []
                image_list = chapter.get('images', [])
                for idx, img_name in enumerate(image_list, 1):
                    img_url = cls._build_image_url(photo_id, img_name)
                    images.append(JmImage(
                        url=img_url,
                        filename=img_name,
                        index=idx
                    ))
                
                photos.append(JmPhoto(
                    photo_id=photo_id,
                    title=photo_title,
                    sort=int(sort),
                    images=images
                ))
        
        if not photos:
            images = []
            image_list = data.get('images', [])
            for idx, img_name in enumerate(image_list, 1):
                img_url = cls._build_image_url(album_id, img_name)
                images.append(JmImage(
                    url=img_url,
                    filename=img_name,
                    index=idx
                ))
            
            photos.append(JmPhoto(
                photo_id=album_id,
                title=title,
                sort=1,
                images=images
            ))
        
        return JmAlbum(
            album_id=album_id,
            title=title,
            author=author,
            authors=authors,
            tags=tags,
            photos=photos,
            cover_url=cls._build_cover_url(album_id),
            page_count=int(data.get('page_count', 0)),
            views=cls._decode_chinese(str(data.get('total_views', ''))),
            likes=cls._decode_chinese(str(data.get('likes', ''))),
            description=description
        )
    
    @classmethod
    def _build_image_url(cls, photo_id: str, img_name: str) -> str:
        domain = random.choice(cls.CDN_DOMAINS)
        return f'https://{domain}/media/photos/{photo_id}/{img_name}'
    
    @classmethod
    def _build_cover_url(cls, album_id: str) -> str:
        return cls._build_image_url(album_id, 'cover.jpg')