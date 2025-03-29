from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

class ProfessionBase(BaseModel):
    name: str = Field(min_length=3, max_length=50)

class ProfessionCreate(ProfessionBase):
    pass

class ProfessionResponse(ProfessionBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes: True

class ProfessionUpdate(ProfessionBase):
    active: Optional[bool] = None

class BusinessTypeLoadOnly(BaseModel):
    id: int
    name: str

class ProfessionWithBusinessTypesResponse(ProfessionResponse):
    business_types: Optional[List[BusinessTypeLoadOnly]] = []