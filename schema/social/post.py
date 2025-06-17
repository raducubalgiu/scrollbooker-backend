from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, condecimal
from backend.models import Hashtag
from backend.schema.social.hashtag import HashtagResponse
from backend.schema.social.post_media import PostMediaBase
from backend.schema.user.user import UserBaseMinimum

class PostFixedSlots(BaseModel):
    start_time: datetime
    end_time: datetime
    is_booked: bool = False

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    business_type_id: int

    product_name: str = Field(max_length=100)
    product_description: str = Field(max_length=200)
    product_duration: int
    product_price: condecimal(gt=0, max_digits=10, decimal_places=2)
    product_price_with_discount: condecimal(gt=0, max_digits=10, decimal_places=2)
    product_discount: condecimal(lt=100, max_digits=5, decimal_places=2) = Decimal("00.00")
    product_currency: str = Field(min_length=3, max_length=3)

    hashtags: Optional[List[str]] = []
    mentions: Optional[List[int]] = []

    description: Optional[str] = None
    product_id: Optional[int] = None

    instant_booking: bool = True
    bookable: Optional[bool] = True

    is_last_minute: Optional[bool] = False
    has_fixed_slots: Optional[bool] = False
    fixed_slots: Optional[List[PostFixedSlots]] = []
    last_minute_end: Optional[datetime] = None

    class Config:
        from_attributes = True

class PostCreate(PostBase):
    media_files: List[PostMediaBase]

class PostResponse(PostBase):
    id: int
    user_id: int
    like_count: bool
    share_count: bool
    comment_count: bool
    save_count: bool

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PostProduct(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    duration: int
    price: condecimal()
    price_with_discount: condecimal()
    discount: condecimal()
    currency: str

    class Config:
        from_attributes = True

class PostCounters(BaseModel):
    comment_count: int
    like_count: int
    save_count: int
    share_count: int

    class Config:
        from_attributes = True

class LastMinute(BaseModel):
    is_last_minute: bool
    last_minute_end: Optional[datetime] = None
    has_fixed_slots: bool
    fixed_slots: Optional[List[PostFixedSlots]] = []

    class Config:
        from_attributes = True

class UserPostResponse(BaseModel):
    id: int
    description: Optional[str] = None
    user: UserBaseMinimum
    product: PostProduct
    counters: PostCounters
    mentions: Optional[List[UserBaseMinimum]] = []
    hashtags: Optional[List[HashtagResponse]] = []
    bookable: bool
    instant_booking: bool
    last_minute: LastMinute
    created_at: datetime

    class Config:
        from_attributes = True