from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_serializer

from schema.user.user import UserBaseMinimum

class NotificationBase(BaseModel):
    type: str = Field(min_length=3, max_length=50)
    sender_id: int
    receiver_id: int

class NotificationCreate(NotificationBase):
    pass

class NotificationEmploymentData(BaseModel):
    employment_request_id: int
    profession_id: int

class NotificationResponse(NotificationBase):
    id: int
    data: Optional[Union[NotificationEmploymentData, Dict[str, Any]]] = None
    message: Optional[str] = None
    is_read: bool
    is_deleted: bool
    sender: UserBaseMinimum = None
    is_follow: bool

    @field_serializer("data")
    def serialize_data(self, data: Optional[Dict[str, Any]], _info ):
        if not data:
            return None
        return data

    class Config:
        from_attributes = True