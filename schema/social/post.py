from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from backend.schema.social.post_media import PostMediaResponse

class PostBase(BaseModel):
    description: str = Field(max_length=500)
    bookable: bool = Field(default=False)
    user_id: int
    product_id: Optional[int] = None
    media_files: List[PostMediaResponse]
    hashtags: Optional[List[str]] = []
    mentions: Optional[List[int]] = []
    expiration_time: Optional[datetime] = None

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    like_count: int
    comment_count: int
    comment_count: int
    share_count: int
    created_at: datetime
    updated_at: datetime