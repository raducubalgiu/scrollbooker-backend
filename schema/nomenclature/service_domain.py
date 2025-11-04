from typing import Optional
from pydantic import Field, BaseModel
from datetime import datetime

class ServiceDomainCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    business_domain_id: int

class ServiceDomainUpdate(BaseModel):
    name: Optional[str] = None
    business_domain_id: int

class ServiceDomainResponse(BaseModel):
    id: int
    name: str
    business_domain_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True