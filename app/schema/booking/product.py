from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from app.schema.booking.nomenclature.sub_filter import SubFilterResponse, SubFilterWithFilterResponse

class ProductBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=3, max_length=255)
    duration: int
    price: float
    service_id: int
    business_id: int
    discount: Optional[float] = Field(default=0)

class ProductUpdate(ProductBase):
    pass

class ProductCreate(ProductBase):
    price_with_discount: Optional[float] = Field(default=0)

class ProductCreateWithSubFilters(BaseModel):
    product: ProductCreate
    sub_filters: List[int]

class ProductResponse(ProductBase):
    id: int
    user_id: int
    price_with_discount: float
    discount: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProductWithSubFiltersResponse(ProductResponse):
    sub_filters: List[SubFilterWithFilterResponse]

