from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

from schema.booking.product import ProductResponse
from schema.booking.schedule import ScheduleResponse
from schema.user.user_counters import UserCountersBase

class UserBaseMinimum(BaseModel):
    id: int
    fullname: Optional[str] = None
    username: str = None
    profession: Optional[str] = None
    avatar: Optional[str] = None
    is_follow: Optional[bool] = None

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    id: int
    fullname: Optional[str] = Field(max_length=30)
    username: str = Field(min_length=3, max_length=35)
    bio: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    date_of_birth: Optional[datetime] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    last_known_lat: Optional[float] = None
    last_known_lng: Optional[float] = None
    active: bool = Field(default=True)
    employee_business_id: Optional[int] = None
    role_id: int

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    schedules: Optional[List[ScheduleResponse]] = []
    products: Optional[List[ProductResponse]] = []

    class Config:
        from_attributes = True

class FullNameUpdate(BaseModel):
    fullname: str = Field(max_length=30)

class UsernameUpdate(BaseModel):
    username: str = Field(max_length=35)

class BioUpdate(BaseModel):
    bio: str = Field(None, max_length=100)

class GenderUpdate(BaseModel):
    gender: str = Field(max_length=30)

class OpeningHours(BaseModel):
    open_now: bool
    closing_time: Optional[str] = None
    next_open_day: Optional[str] = None
    next_open_time: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: int
    username: str
    fullname: Optional[str]
    avatar: Optional[str] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    business_id: Optional[int] = None
    business_type_id: Optional[int] = None
    counters: UserCountersBase
    profession: str
    opening_hours: OpeningHours
    is_follow: bool
    business_owner: Optional[UserBaseMinimum] = None

    class Config:
        from_attributes = True