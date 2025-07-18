from typing import Optional, List

from pydantic import BaseModel, Field
from datetime import datetime

class BusinessTypeBase(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    plural: str = Field(min_length=3, max_length=50)
    business_domain_id: int

class BusinessTypeCreate(BusinessTypeBase):
    pass

class BusinessTypeResponse(BusinessTypeBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BusinessTypeUpdate(BaseModel):
    name: Optional[str] = None
    plural: Optional[str] = None
    business_domain_id: Optional[int] = None
    active: Optional[bool] = None

class ProfessionLoadOnly(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ServiceLoadOnly(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class FilterLoadOnly(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class SubFilterLoadOnly(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class FilterWithSubFilters(FilterLoadOnly):
    sub_filters: Optional[List[SubFilterLoadOnly]] = []

    class Config:
        from_attributes = True

class BusinessTypeWithProfessionsResponse(BusinessTypeResponse):
    professions: Optional[List[ProfessionLoadOnly]] = []

class BusinessTypeWithServicesAndFiltersResponse(BusinessTypeResponse):
    services: Optional[List[ServiceLoadOnly]] = []
    filters: Optional[List[FilterWithSubFilters]] = []

