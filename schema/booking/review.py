from typing import Optional, List
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

class RatingBreakdown(BaseModel):
    rating: int
    count: int

class ReviewSummaryResponse(BaseModel):
    average_rating: float
    total_reviews: int
    breakdown: List[RatingBreakdown]

class ReviewCustomer(BaseModel):
    id: int
    username: str
    fullname: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True

class ReviewService(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ReviewProduct(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class UserReviewResponse(BaseModel):
    id: int
    rating: int
    review: str
    customer: ReviewCustomer
    service: ReviewService
    product: ReviewProduct
    like_count: bool
    is_liked: bool
    is_liked_by_author: bool
    created_at: datetime

    class Config:
        from_attributes = True
