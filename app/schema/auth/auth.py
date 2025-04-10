from typing import Optional

from pydantic import BaseModel, Field, EmailStr
from app.schema.user.user import UserBase
from app.schema.user.user_counters import UserCountersBase

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(min_length=6, max_length=255)
    role_name: str

class UserRegisterResponse(UserBase):
    id: int

class UserInfoResponse(BaseModel):
    id: int
    fullname: Optional[str] = None
    avatar: Optional[str] = None
    username: str
    business_id: Optional[int] = None
    email: EmailStr
    counters: UserCountersBase
    profession: str

    class Config:
        from_attributes = True


