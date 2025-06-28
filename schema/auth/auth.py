from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationError
from schema.user.user import UserBase

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=20)
    role_name: str

    @field_validator("password", mode="after")
    def validate_password(cls, value: str) -> str:
        if not (c.isupper() for c in value):
            raise ValueError("The password should contain at least 1 uppercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("The password should contain at least 1 digit")
        return value

class UserRegisterResponse(UserBase):
    id: int

class UserInfoResponse(BaseModel):
    id: int
    business_id: Optional[int] = None
    business_type_id: Optional[int] = None
    is_validated: bool
    registration_step: Optional[str] = None

    class Config:
        from_attributes = True

class UserInfoUpdate(BaseModel):
    username: str = Field(min_length=3, max_length=35)
    fullname: Optional[str] = Field(max_length=30)
    bio: str
    profession: str

