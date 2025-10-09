from decimal import Decimal

from pydantic import BaseModel, Field, EmailStr, field_serializer
from typing import Optional, List
from datetime import datetime, date
from core.enums.gender_type_enum import GenderTypeEnum
from core.enums.registration_step_enum import RegistrationStepEnum
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
    ratings_average: Optional[Decimal] = None

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    id: int
    fullname: Optional[str] = Field(max_length=35)
    username: str = Field(min_length=3, max_length=35)
    bio: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    date_of_birth: Optional[datetime] = None
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
    fullname: str = Field(min_length=3, max_length=35)

class UsernameUpdate(BaseModel):
    username: str = Field(min_length=3, max_length=35)

class BirthDateUpdate(BaseModel):
    birthdate: Optional[str] = None

class GenderUpdate(BaseModel):
    gender: GenderTypeEnum

class BioUpdate(BaseModel):
    bio: str = Field(None, min_length=3, max_length=100)

class WebsiteUpdate(BaseModel):
    website: str = Field(None, min_length=3, max_length=255)

class PublicEmailUpdate(BaseModel):
    public_email: str = Field(None, min_length=3, max_length=100)

class UserUpdateResponse(BaseModel):
    id: int
    fullname: str
    username: str
    bio: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    website: Optional[str] = None
    public_email: Optional[str] = None

class UserAuthStateResponse(BaseModel):
    is_validated: bool
    registration_step: Optional[RegistrationStepEnum] = None

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

    website: Optional[str] = None
    public_email: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    tiktok: Optional[str] = None

    business_id: Optional[int] = None
    business_type_id: Optional[int] = None
    counters: UserCountersBase
    profession: str

    opening_hours: OpeningHours
    is_follow: bool
    business_owner: Optional[UserBaseMinimum] = None
    is_own_profile: bool
    is_business_or_employee: bool
    distance_km: Optional[float] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True

class SearchUsername(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=35,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Must be 3-35 characters, only letters, numbers, and underscores"
    )

class SearchUsernameResponse(BaseModel):
    available: bool
    suggestions: Optional[List[str]] = []