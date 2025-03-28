from pydantic import BaseModel
from typing import Optional, List

from app.schema.booking.nomenclature.service import ServiceResponse
from app.schema.user.user import UserResponse

class BusinessBase(BaseModel):
    description: Optional[str] = None
    address: str
    location: tuple[float, float]
    owner_id: int = None

    class Config:
        from_attributes: True

class BusinessCreate(BusinessBase):
    pass

class BusinessResponse(BusinessBase):
    id: int
    business_owner: Optional[UserResponse] = None
    employees: Optional[List[UserResponse]] = []
    services: Optional[List[ServiceResponse]] = []
    distance: Optional[str] = None
    timezone: str

    class Config:
        from_attributes: True

class BusinessByDistanceResponse(BaseModel):
    id: int
    description: str
    # products: Optional[List[ProductResponse]] = []
    # schedule: List[ScheduleResponse] = []
    # services: Optional[List[ServiceResponse]] = []
    #appointments: Optional[List[AppointmentResponse]] = []
    distance: str

