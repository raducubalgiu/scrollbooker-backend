from typing import Optional
from pydantic import Field, BaseModel
from datetime import datetime

class BusinessDomainBase(BaseModel):
    name: str = Field(min_length=5, max_length=255)

class BusinessDomainCreate(BusinessDomainBase):
    pass

class BusinessDomainResponse(BusinessDomainBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes: True

class BusinessDomainUpdate(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None