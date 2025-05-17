from typing import Optional, List
from pydantic import BaseModel, Field, condecimal
from datetime import datetime
from decimal import Decimal
from backend.schema.nomenclature.sub_filter import SubFilterWithFilterResponse

class ProductBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=3, max_length=255)
    duration: int
    service_id: int
    business_id: int
    currency_id: int
    price: condecimal(gt=0, max_digits=10, decimal_places=2)
    price_with_discount: condecimal(gt=0, max_digits=10, decimal_places=2)
    discount: condecimal(lt=100, max_digits=5, decimal_places=2) = Decimal("00.00")

class ProductUpdate(ProductBase):
    pass

class ProductCreate(ProductBase):
    pass

class ProductCreateWithSubFilters(BaseModel):
    product: ProductCreate
    sub_filters: List[int]

class ProductResponse(ProductBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProductWithSubFiltersResponse(ProductResponse):
    sub_filters: List[SubFilterWithFilterResponse]

    class Config:
        from_attributes = True

