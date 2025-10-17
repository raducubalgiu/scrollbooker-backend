from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CommentBase(BaseModel):
    text: str = Field(min_length=1, max_length=200)
    parent_id: Optional[int] = None

class CommentCreate(CommentBase):
    pass

class CommentUser(BaseModel):
    id: int
    fullname: str
    username: str
    avatar: Optional[str] = None

class CommentResponse(CommentBase):
    id: int
    user: CommentUser
    post_id: int
    like_count: int
    is_liked: bool
    liked_by_post_author: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
