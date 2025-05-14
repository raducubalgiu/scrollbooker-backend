from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field

from backend.schema.user.user import UserBaseMinimum


class NotificationBase(BaseModel):
    type: str = Field(min_length=3, max_length=50)
    sender_id: int
    receiver_id: int

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    is_read: bool
    is_deleted: bool
    sender: UserBaseMinimum = None

    class Config:
        from_attributes = True