from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class CharacterBase(BaseModel):
    name: str
    avatar_url: Optional[str] = None

class CharacterOut(CharacterBase):
    id: int
    slug: str
    created_at: str
    last_searched_at: Optional[str] = None
    total_candidates: int = 0
    total_favorites: int = 0

class ImageOut(BaseModel):
    id: int
    character_id: int
    filename: str
    rating: Optional[str] = "sfw"  # sfw, r18
    batch_number: Optional[int] = 1
    task_id: Optional[str] = None
    temp_url: Optional[str] = None
    favorites_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    original_source: Optional[str] = None
    source_url: Optional[str] = None
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    title: Optional[str] = None
    copyright_info: Optional[str] = None
    width: int = 0
    height: int = 0
    file_size: int = 0
    phash: Optional[str] = None
    status: str = "pending"  # pending, saved, deleted, cleaned
    download_time: Optional[str] = None
    saved_time: Optional[str] = None

class TaskCreate(BaseModel):
    character_name: str
    limit: int = Field(default=100, ge=1, le=300)
    rating: str = Field(default="sfw", description="Rating attribute: 'sfw' (全年龄, 无R18) or 'r18' (R-18, 无全年龄)")
    sources: Optional[List[str]] = None

class TaskOut(BaseModel):
    id: str
    character_name: str
    character_id: Optional[int] = None
    rating: Optional[str] = "sfw"
    status: str
    progress_current: int
    progress_total: int
    progress_message: Optional[str] = None
    result_count: int = 0
    error_message: Optional[str] = None
    created_at: str
    updated_at: str

class BatchActionRequest(BaseModel):
    image_ids: List[int]
    action: str  # save, delete, favorite, clean

class SettingUpdate(BaseModel):
    settings: Dict[str, str]

class ImageCandidate(BaseModel):
    image_url: str
    source_url: str
    source_name: str
    source_id: Optional[str] = None
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    title: Optional[str] = None
    copyright_info: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    preview_url: Optional[str] = None
    rating: Optional[str] = "sfw"  # sfw, r18
    score: Optional[int] = 0
    tags: Optional[List[str]] = []
    headers: Optional[Dict[str, str]] = None
