from typing import Optional
from pydantic import BaseModel, condecimal, Field
from datetime import datetime

class AppointmentBase(BaseModel):
    start_date: datetime
    end_date: datetime
    customer_id: Optional[int] = None
    customer_username: str = Field(min_length=3, max_length=50)
    user_id: int
    product_id: int
    business_id: int
    service_id: int
    service_name: str
    channel: str
    currency: str = Field(min_length=3, max_length=3)
    product_price: condecimal(gt=0, max_digits=10, decimal_places=2)
    is_blocked: Optional[bool] = False
    instant_booking: Optional[bool] = True

class AppointmentCreate(AppointmentBase):
    pass

    class Config:
        from_attributes = True

class AppointmentBlockedCreate(BaseModel):
    block_message: str = Field(min_length=3, max_length=50)
    start_date: datetime
    end_date: datetime
    user_id: int

class AppointmentResponse(AppointmentBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True