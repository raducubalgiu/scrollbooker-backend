from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, condecimal

from backend.schema.social.post_media import PostMediaBase, PostMediaResponse

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