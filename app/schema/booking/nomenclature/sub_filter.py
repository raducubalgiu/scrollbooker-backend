from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SubFilterBase(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    filter_id: int

class SubFilterCreate(SubFilterBase):
    active: Optional[bool] = None

class SubFilterResponse(SubFilterBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class SubFilterUpdate(BaseModel):
    name: Optional[str] = None
    filter_id: Optional[int] = None
    active: Optional[bool] = None
