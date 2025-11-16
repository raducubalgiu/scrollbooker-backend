from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from schema.social.hashtag import HashtagResponse
from schema.social.post_media import PostMediaBase, PostMediaResponse

class PostFixedSlots(BaseModel):
    start_time: datetime
    end_time: datetime
    is_booked: bool = False

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    business_type_id: int
    business_id: int
    employee_id: Optional[int] = None

    hashtags: Optional[List[str]] = []
    mentions: Optional[List[int]] = []

    description: Optional[str] = None
    product_id: Optional[int] = None

    is_video_review: Optional[bool] = False
    rating: Optional[int] = None
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

    like_count: int
    repost_count: int
    comment_count: int
    bookmark_count: int
    bookings_count: int

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PostProductCurrency(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class PostProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    duration: int
    price: Decimal
    price_with_discount: Decimal
    discount: Decimal
    currency: PostProductCurrency

    class Config:
        from_attributes = True

class PostCounters(BaseModel):
    comment_count: int
    like_count: int
    bookmark_count: int
    repost_count: int
    bookings_count: int

    class Config:
        from_attributes = True

class LastMinute(BaseModel):
    is_last_minute: bool
    last_minute_end: Optional[datetime] = None
    has_fixed_slots: bool
    fixed_slots: Optional[List[PostFixedSlots]] = []

    class Config:
        from_attributes = True

class PostUser(BaseModel):
    id: int
    fullname: str
    username: str
    profession: str
    avatar: Optional[str] = None
    is_follow: bool
    ratings_average: float
    ratings_count: int

class PostUserActions(BaseModel):
    is_liked: bool
    is_reposted: bool
    is_bookmarked: bool

class PostBusinessOwner(BaseModel):
    id: int
    fullname: str
    avatar: Optional[str] = None
    ratings_average: float

class PostEmployee(BaseModel):
    id: int
    fullname: str
    avatar: Optional[str] = None

class UserPostResponse(BaseModel):
    id: int
    description: Optional[str] = None
    user: PostUser
    business_owner: PostBusinessOwner
    employee: Optional[PostEmployee] = None
    counters: PostCounters
    media_files: List[PostMediaResponse]
    user_actions: PostUserActions
    hashtags: Optional[List[HashtagResponse]] = []
    business_id: Optional[int] = None
    is_video_review: bool
    rating: Optional[int] = None
    bookable: bool
    last_minute: LastMinute
    created_at: datetime

    class Config:
        from_attributes = True