from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class FilterBase(BaseModel):
    name: str = Field(min_length=3, max_length=50)

class FilterCreate(FilterBase):
    active: Optional[bool] = None

class FilterResponse(FilterBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FilterUpdate(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None

class SubFilterLoadOnly(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class FilterWithSubFiltersResponse(FilterResponse):
    sub_filters: Optional[List[SubFilterLoadOnly]] = []
