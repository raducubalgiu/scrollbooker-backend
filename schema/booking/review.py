from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class ReviewCreate(BaseModel):
    review: str = Field(max_length=500)
    rating: int = Field(gt=0, lt=6)
    user_id: int
    product_id: int
    parent_id: Optional[int] = None

class ReviewUpdate(BaseModel):
    review: str = Field(max_length=500)
    rating: int = Field(gt=0, lt=6)

class ReviewResponse(BaseModel):
    id: int
    review: str
    rating: int
    customer_id: int
    user_id: int
    service_id: int
    product_id: int
    appointment_id: int
    parent_id: Optional[int] = None

    created_at: datetime

    class Config:
        from_attributes = True

class RatingBreakdown(BaseModel):
    rating: int
    count: int

class ReviewSummaryResponse(BaseModel):
    average_rating: float
    total_reviews: int
    breakdown: List[RatingBreakdown]

class ReviewBusinessOwner(BaseModel):
    id: int
    username: str
    fullname: str
    avatar: Optional[str] = None

    class Config:
        from_attributes = True

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
    product_business_owner: ReviewBusinessOwner
    customer: ReviewCustomer
    service: ReviewService
    product: ReviewProduct
    like_count: int
    is_liked: bool
    is_liked_by_product_owner: bool
    created_at: datetime

    class Config:
        from_attributes = True
