from typing import Optional, List
from pydantic import BaseModel, Field, condecimal
from datetime import datetime
from decimal import Decimal
from schema.nomenclature.sub_filter import SubFilterWithFilterResponse

class ProductBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=3, max_length=255)
    duration: int
    service_id: int
    business_id: int
    currency_id: int
    price: Decimal
    price_with_discount: Decimal
    discount: Decimal

class ProductUpdate(ProductBase):
    pass

class ProductCreate(ProductBase):
    pass

class ProductCreateWithSubFilters(BaseModel):
    product: ProductCreate
    sub_filters: List[int]

class ProductSubFilter(BaseModel):
    id: int
    name: str

class ProductResponse(ProductBase):
    id: int
    user_id: int
    sub_filters: List[SubFilterWithFilterResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProductWithSubFiltersResponse(ProductResponse):
    sub_filters: List[SubFilterWithFilterResponse]

    class Config:
        from_attributes = True

