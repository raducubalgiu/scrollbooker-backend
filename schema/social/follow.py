from pydantic import BaseModel
from datetime import datetime

class FollowResponse(BaseModel):
    id: int
    followee_id: int
    follower_id: int
    created_at: datetime

    class Config:
        from_attributes = True


