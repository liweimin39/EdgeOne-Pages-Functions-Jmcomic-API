# cloud-functions/api/utils/parser.py
import random
import logging
from typing import Dict, List, Optional
from .models import JmAlbum, JmPhoto, JmImage

logger = logging.getLogger(__name__)


class JmParser:
    """禁漫数据解析器"""
    
    # CDN 域名池
    CDN_DOMAINS = [
        'cdn-msp.jmapiproxy1.cc',
        'cdn-msp.jmapiproxy2.cc',
        'cdn-msp3.jmapiproxy2.cc',
        'cdn-msp4.jmapiproxy.cc',
        'cdn-msp5.jmapiproxy.cc',
    ]
    
    @classmethod
    def _decode_chinese(cls, text: str) -> str:
        """将禁漫 API 返回的乱码正确解码为中文"""
        if not text:
            return text
        
        if not isinstance(text, str):
            text = str(text)
        
        try:
            return text.encode('latin1').decode('gbk')
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                return text.encode('latin1').decode('gb2312')
            except (UnicodeEncodeError, UnicodeDecodeError):
                try:
                    return text.encode('latin1').decode('utf-8')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    logger.warning(f"无法解码文本: {text[:50]}...")
                    return text
    
    @classmethod
    def _decode_text_safe(cls, text: str) -> str:
        """安全解码文本"""
        if not text:
            return ''
        try:
            return cls._decode_chinese(text)
        except Exception as e:
            logger.warning(f"解码失败: {e}")
            return str(text)
    
    @classmethod
    def _build_image_url(cls, photo_id: str, img_name: str) -> str:
        """构建图片 CDN URL"""
        domain = random.choice(cls.CDN_DOMAINS)
        return f'https://{domain}/media/photos/{photo_id}/{img_name}'
    
    @classmethod
    def _build_cover_url(cls, album_id: str) -> str:
        """构建封面 URL"""
        domain = random.choice(cls.CDN_DOMAINS)
        return f'https://{domain}/media/photos/{album_id}/cover.jpg'
    
    @classmethod
    def parse_album(cls, data: Dict) -> JmAlbum:
        """解析本子数据"""
        try:
            album_id = str(data.get('id', ''))
            title = cls._decode_text_safe(data.get('name', ''))
            description = cls._decode_text_safe(data.get('description', ''))
            
            # 解析作者
            authors_data = data.get('author', [])
            if isinstance(authors_data, str):
                authors = [cls._decode_text_safe(authors_data)] if authors_data else []
            elif isinstance(authors_data, list):
                authors = [cls._decode_text_safe(a) for a in authors_data if a]
            else:
                authors = []
            
            author = authors[0] if authors else '未知'
            
            # 解析标签
            tags_data = data.get('tags', [])
            if isinstance(tags_data, str):
                tags = [cls._decode_text_safe(t) for t in tags_data.split() if t]
            elif isinstance(tags_data, list):
                tags = [cls._decode_text_safe(t) for t in tags_data if t]
            else:
                tags = []
            
            # 解析章节列表
            photos = []
            series = data.get('series', [])
            
            if series:
                for chapter in series:
                    photo_id = str(chapter.get('id', ''))
                    photo_title = cls._decode_text_safe(chapter.get('name', ''))
                    
                    # ★ 修复：安全处理 sort 字段
                    sort_raw = chapter.get('sort', '1')
                    try:
                        sort = int(sort_raw) if sort_raw else 1
                    except (ValueError, TypeError):
                        sort = 1
                    
                    # 解析图片列表
                    images = []
                    image_list = chapter.get('images', [])
                    if image_list:
                        for idx, img_name in enumerate(image_list, 1):
                            if img_name:
                                img_url = cls._build_image_url(photo_id, img_name)
                                images.append(JmImage(
                                    url=img_url,
                                    filename=img_name,
                                    index=idx
                                ))
                    
                    if photo_id:
                        photos.append(JmPhoto(
                            photo_id=photo_id,
                            title=photo_title,
                            sort=sort,
                            images=images
                        ))
            
            # 如果没有章节，尝试从当前数据解析图片
            if not photos:
                images = []
                image_list = data.get('images', [])
                if image_list:
                    for idx, img_name in enumerate(image_list, 1):
                        if img_name:
                            img_url = cls._build_image_url(album_id, img_name)
                            images.append(JmImage(
                                url=img_url,
                                filename=img_name,
                                index=idx
                            ))
                
                if album_id:
                    photos.append(JmPhoto(
                        photo_id=album_id,
                        title=title,
                        sort=1,
                        images=images
                    ))
            
            # 解析统计数据
            page_count = data.get('page_count', 0)
            try:
                page_count = int(page_count) if page_count else 0
            except (ValueError, TypeError):
                page_count = 0
            
            views = cls._decode_text_safe(str(data.get('total_views', '')))
            likes = cls._decode_text_safe(str(data.get('likes', '')))
            
            return JmAlbum(
                album_id=album_id,
                title=title,
                author=author,
                authors=authors,
                tags=tags,
                photos=photos,
                cover_url=cls._build_cover_url(album_id),
                page_count=page_count,
                views=views,
                likes=likes,
                description=description
            )
            
        except Exception as e:
            logger.error(f"解析本子数据失败: {e}", exc_info=True)
            return JmAlbum(
                album_id=str(data.get('id', '')),
                title='解析失败',
                author='未知',
                authors=[],
                tags=[],
                photos=[]
            )
    
    @classmethod
    def parse_photo(cls, data: Dict, photo_id: str) -> Dict:
        """解析章节图片数据"""
        try:
            logger.info(f"解析章节数据: {photo_id}")
            
            # 直接从 data 中获取图片列表
            images = data.get('images', [])
            
            # 如果 images 为空，尝试从其他字段获取
            if not images:
                images = data.get('img_list', []) or data.get('image_list', [])
                logger.info(f"尝试从其他字段获取图片: {len(images)} 张")
            
            logger.info(f"获取到图片列表: {len(images)} 张")
            
            if not images:
                return {
                    'photo_id': photo_id,
                    'title': cls._decode_text_safe(data.get('name', '')),
                    'image_count': 0,
                    'images': []
                }
            
            image_list = []
            for idx, img_name in enumerate(images, 1):
                if img_name:
                    img_url = cls._build_image_url(photo_id, img_name)
                    image_list.append({
                        'index': idx,
                        'filename': img_name,
                        'url': img_url
                    })
            
            result = {
                'photo_id': photo_id,
                'title': cls._decode_text_safe(data.get('name', '')),
                'image_count': len(image_list),
                'images': image_list
            }
            
            logger.info(f"解析完成: {result['image_count']} 张图片")
            return result
            
        except Exception as e:
            logger.error(f"解析章节数据失败: {e}", exc_info=True)
            return {
                'photo_id': photo_id,
                'title': '',
                'image_count': 0,
                'images': []
            }