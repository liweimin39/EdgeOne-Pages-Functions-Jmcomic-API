# cloud-functions/api/utils/models.py
"""数据模型定义"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class JmImage:
    """图片信息"""
    url: str
    filename: str
    index: int
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'url': self.url,
            'filename': self.filename,
            'index': self.index
        }


@dataclass
class JmPhoto:
    """章节信息"""
    photo_id: str
    title: str
    sort: int
    images: List[JmImage] = field(default_factory=list)
    scramble_id: str = ""
    
    def to_dict(self, include_images: bool = False) -> dict:
        """
        转换为字典
        
        Args:
            include_images: 是否包含图片列表（默认 False，用于 album 接口）
        """
        result = {
            'photo_id': self.photo_id,
            'title': self.title,
            'sort': self.sort,
        }
        
        # 只在需要时返回图片列表
        if include_images:
            result['image_count'] = len(self.images)
            result['images'] = [img.to_dict() for img in self.images]
        
        return result


@dataclass
class JmAlbum:
    """本子信息"""
    album_id: str
    title: str
    author: str
    authors: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    photos: List[JmPhoto] = field(default_factory=list)
    cover_url: str = ""
    page_count: int = 0
    views: str = ""
    likes: str = ""
    description: str = ""
    
    def to_dict(self, include_images: bool = False) -> dict:
        """
        转换为字典
        
        Args:
            include_images: 是否包含图片列表（默认 False，用于 album 接口）
        """
        return {
            'album_id': self.album_id,
            'album_title': self.title,
            'author': self.author,
            'authors': self.authors,
            'tags': self.tags,
            'cover_url': self.cover_url,
            'views': self.views,
            'likes': self.likes,
            'page_count': self.page_count,
            'description': self.description,
            'total_photos': len(self.photos),
            'photos': [photo.to_dict(include_images=include_images) for photo in self.photos]
        }