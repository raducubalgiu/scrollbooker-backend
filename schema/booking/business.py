from pydantic import BaseModel
from typing import Optional, List

from schema.nomenclature.service import ServiceResponse
from schema.user.user import UserAuthStateResponse, UserBaseMinimum

class BusinessCoordinates(BaseModel):
    lat: float
    lng: float

class BusinessBase(BaseModel):
    description: Optional[str] = None
    address: str
    coordinates: BusinessCoordinates
    owner_id: int = None
    business_type_id: int
    has_employees: bool

class BusinessCreate(BaseModel):
    description: Optional[str] = None
    place_id: str
    business_type_id: int
    owner_fullname: str

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

class BusinessHasEmployeesUpdate(BaseModel):
    has_employees: bool

class BusinessCreateResponse(BaseModel):
    authState: UserAuthStateResponse
    business_id: int

class RecommendedBusinessesResponse(BaseModel):
    user: UserBaseMinimum
    distance: Optional[float] = None
    is_open: bool




