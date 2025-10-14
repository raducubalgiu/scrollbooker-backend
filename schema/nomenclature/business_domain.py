from typing import Optional, List
from pydantic import Field, BaseModel
from datetime import datetime

from schema.nomenclature.business_type import BusinessTypeResponse


class BusinessDomainCreate(BaseModel):
    name: str = Field(min_length=5, max_length=255)
    short_name: str = Field(min_length=3, max_length=50)

class BusinessDomainResponse(BaseModel):
    id: int
    name: str
    short_name: str
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BusinessDomainsWithBusinessTypes(BusinessDomainResponse):
    business_types: List[BusinessTypeResponse]

class BusinessDomainUpdate(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None