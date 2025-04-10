from typing import Optional

from pydantic import BaseModel
from datetime import datetime

from app.schema.user.user import UserBaseMinimum

class FollowBase(BaseModel):
    follower_id: int
    followee_id: int

class FollowResponse(BaseModel):
    id: int
    created_at: datetime
    followee: Optional[UserBaseMinimum] = None
    follower: Optional[UserBaseMinimum] = None

    class Config:
        from_attributes = True


