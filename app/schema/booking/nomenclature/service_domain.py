from typing import Optional, List
from pydantic import Field, BaseModel
from datetime import datetime

class ServiceDomainBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)

class ServiceDomainCreate(ServiceDomainBase):
    pass

class ServiceDomainResponse(ServiceDomainBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes: True

class ServiceDomainUpdate(BaseModel):
    name: Optional[str] = None

class ServiceLoadOnly(BaseModel):
    id: int
    name: str

class ServiceDomainWithServices(ServiceDomainResponse):
    services: Optional[List[ServiceLoadOnly]] = []