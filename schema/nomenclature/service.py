from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from schema.user.user import UserBaseMinimum


class ServiceBase(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    business_domain_id: int
    keywords: List[str] = []

    class Config:
        from_attributes = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    keywords: Optional[List[str]] = None
    active: Optional[bool] = None

class ServiceResponse(ServiceBase):
    id: int
    active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ServiceWithEmployeesResponse(BaseModel):
    service: ServiceResponse
    products_count: int
    employees: List[UserBaseMinimum] = []

class Filter(BaseModel):
    id: int
    name: str

class ServiceWithFiltersResponse(ServiceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    filters: List[Filter]

    class Config:
        from_attributes = True

class ServiceIdsUpdate(BaseModel):
    service_ids: List[int]