from typing import Optional
from pydantic import BaseModel, HttpUrl

from backend.core.enums.media_type_enum import MediaTypeEnum

class PostMediaBase(BaseModel):
    url: str
    type: MediaTypeEnum
    thumbnail_url: str
    duration: Optional[float] = None

class PostMediaCreate(PostMediaBase):
    post_id: int
    order_index: int

class PostMediaResponse(PostMediaBase):
    id: int
    post_id: int
    order_index: int

    class Config:
        from_attributes = True