from pydantic import BaseModel
from typing import Optional, List

from schema.nomenclature.service import ServiceResponse

class BusinessBase(BaseModel):
    description: Optional[str] = None
    address: str
    coordinates: tuple[float, float]
    owner_id: int = None
    business_type_id: int
    has_employees: Optional[bool] = None

class BusinessCreate(BaseModel):
    description: Optional[str] = None
    place_id: str
    owner_id: int = None
    business_type_id: int

class BusinessResponse(BusinessBase):
    id: int
    services: Optional[List[ServiceResponse]] = []
    timezone: str

    class Config:
        from_attributes = True

class BusinessEmployeesResponse(BaseModel):
    id: str
    username: str
    job: str
    followers_count: int
    ratings_count: int
    ratings_average: float
    hire_date: str
    has_employees: bool

    class Config:
        from_attributes = True

class BusinessPlaceAddressResponse(BaseModel):
    description: str
    place_id: str




