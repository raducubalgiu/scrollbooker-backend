from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

from app.schema.booking.product import ProductResponse
from app.schema.booking.schedule import ScheduleResponse

class UserBaseMinimum(BaseModel):
    id: int
    fullname: Optional[str] = None
    username: str = Field(min_length=3, max_length=50)
    avatar: Optional[str] = None
    is_follow: Optional[bool]

    class Config:
        from_attributes: True

class UserBase(BaseModel):
    id: int
    fullname: Optional[str] = Field(min_length=3, max_length=100)
    username: str = Field(min_length=3, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    email: EmailStr
    date_of_birth: Optional[datetime] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    last_known_lat: Optional[float] = None
    last_known_lng: Optional[float] = None
    active: bool = Field(default=True)
    business_employee_id: Optional[int] = None
    role_id: int

    class Config:
        from_attributes: True

class UserResponse(UserBase):
    id: int
    schedules: Optional[List[ScheduleResponse]] = []
    products: Optional[List[ProductResponse]] = []

    class Config:
        from_attributes = True