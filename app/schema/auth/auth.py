from typing import Optional

from pydantic import BaseModel, Field, EmailStr
from app.schema.user.user import UserBase
from app.schema.user.user_counters import UserCountersBase

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=35)
    password: str = Field(min_length=6, max_length=255)
    role_name: str

class UserRegisterResponse(UserBase):
    id: int

class UserInfoResponse(BaseModel):
    id: int
    username: str
    fullname: Optional[str]
    avatar: Optional[str] = None
    business_id: Optional[int] = None
    email: EmailStr
    counters: UserCountersBase
    profession: str

    class Config:
        from_attributes = True

class UserInfoUpdate(BaseModel):
    username: str = Field(min_length=3, max_length=35)
    fullname: Optional[str] = Field(max_length=30)
    bio: str
    profession: str

