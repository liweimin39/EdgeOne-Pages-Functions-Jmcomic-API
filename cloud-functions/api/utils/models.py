"""数据模型定义"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class JmImage:
    """图片信息"""
    url: str
    filename: str
    index: int


@dataclass
class JmPhoto:
    """章节信息"""
    photo_id: str
    title: str
    sort: int
    images: List[JmImage]
    scramble_id: str = ""


@dataclass
class JmAlbum:
    """本子信息"""
    album_id: str
    title: str
    author: str
    authors: List[str]
    tags: List[str]
    photos: List[JmPhoto]
    cover_url: str = ""
    page_count: int = 0
    views: str = ""
    likes: str = ""
    description: str = ""