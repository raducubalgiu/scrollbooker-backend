from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, condecimal
from backend.schema.social.post_media import PostMediaResponse

class PostFixedSlots(BaseModel):
    start_time: datetime
    end_time: datetime
    is_booked: bool = False

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    user_id: int
    business_type_id: int
    is_last_minute: bool
    has_fixed_slots: bool
    media_files: List[PostMediaResponse]

    product_name: str = Field(max_length=100)
    product_description: str = Field(max_length=200)
    product_price: condecimal(gt=0, max_digits=10, decimal_places=2)
    product_price_with_discount: condecimal(gt=0, max_digits=10, decimal_places=2)
    product_discount: condecimal(lt=100, max_digits=5, decimal_places=2) = Decimal("00.00")
    product_currency: str = Field(min_length=3, max_length=3)

    fixed_slots: Optional[List[PostFixedSlots]] = []
    hashtags: Optional[List[str]] = []
    mentions: Optional[List[int]] = []

    description: Optional[str] = None
    product_id: Optional[int] = None
    instant_booking: bool = True
    bookable: bool = Field(default=False)
    last_minute_end: Optional[datetime] = None

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int

    like_count: bool
    share_count: bool
    comment_count: bool
    save_count: bool

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True