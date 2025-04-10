from typing import Optional

from pydantic import BaseModel
from datetime import datetime

class AppointmentBase(BaseModel):
    start_date: datetime
    end_date: datetime

class AppointmentCreate(AppointmentBase):
    product_id: int
    channel: Optional[str] = None

    class Config:
        from_attributes = True

class AppointmentResponse(AppointmentBase):
    id: int
    customer_id: int | None = None
    user_id: int
    business_id: int
    service_id: int | None = None
    product_id: int | None = None
    status: str
    channel: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True