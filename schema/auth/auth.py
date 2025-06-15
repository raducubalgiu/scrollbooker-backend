from typing import Optional

from pydantic import BaseModel, Field, EmailStr
from backend.schema.user.user import UserBase

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=35)
    password: str = Field(min_length=6, max_length=255)
    role_name: str

class UserRegisterResponse(UserBase):
    id: int

class UserInfoResponse(BaseModel):
    id: int
    business_id: Optional[int] = None
    business_type_id: Optional[int] = None

    class Config:
        from_attributes = True

class UserInfoUpdate(BaseModel):
    username: str = Field(min_length=3, max_length=35)
    fullname: Optional[str] = Field(max_length=30)
    bio: str
    profession: str

