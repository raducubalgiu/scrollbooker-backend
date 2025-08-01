from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, condecimal
from schema.social.hashtag import HashtagResponse
from schema.social.post_media import PostMediaBase, PostMediaResponse
from schema.user.user import UserBaseMinimum

class PostFixedSlots(BaseModel):
    start_time: datetime
    end_time: datetime
    is_booked: bool = False

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    business_type_id: int

    product_name: Optional[str] = None
    product_description: Optional[str] = None
    product_duration: Optional[int] = None
    product_price: Optional[Decimal] = None
    product_price_with_discount: Optional[Decimal] = None
    product_discount: Optional[Decimal] = None
    product_currency: Optional[str] = None

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
    bookmark_count: bool

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PostProduct(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    duration: int
    price: Decimal
    price_with_discount: Decimal
    discount: Decimal
    currency: str

    class Config:
        from_attributes = True

class PostCounters(BaseModel):
    comment_count: int
    like_count: int
    bookmark_count: int
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

class PostUserActions(BaseModel):
    is_liked: bool
    is_reposted: bool
    is_bookmarked: bool

class UserPostResponse(BaseModel):
    id: int
    description: Optional[str] = None
    user: UserBaseMinimum
    product: Optional[PostProduct] = None
    counters: PostCounters
    media_files: List[PostMediaResponse]
    user_actions: PostUserActions
    mentions: Optional[List[UserBaseMinimum]] = []
    hashtags: Optional[List[HashtagResponse]] = []
    business_id: Optional[int] = None
    bookable: bool
    instant_booking: bool
    last_minute: LastMinute
    created_at: datetime

    class Config:
        from_attributes = True