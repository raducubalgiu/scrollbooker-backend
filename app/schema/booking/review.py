from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime

class ReviewBase(BaseModel):
    review: str = Field(max_length=500)
    rating: int = Field(gt=0, lt=6)
    user_id: int
    service_id: int
    product_id: int
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    customer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
