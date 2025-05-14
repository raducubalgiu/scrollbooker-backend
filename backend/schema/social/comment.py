from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CommentCreate(BaseModel):
    text: str = Field(min_length=1, max_length=200)
    parent_id: Optional[int] = None

class CommentBase(BaseModel):
    id: int
    post_id: int
    user_id: int
    parent_id: Optional[int] = None
    text: str
    like_count: int
    created_at: datetime
    updated_at: datetime

class CommentResponse(BaseModel):
    id: int
    text: str
    user_id: int
    username: str
    like_count: int
    is_liked: bool
    liked_by_post_author: bool
    created_at: datetime