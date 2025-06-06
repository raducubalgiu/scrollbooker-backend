from typing import Optional
from pydantic import BaseModel, condecimal, Field
from datetime import datetime

from backend.schema.user.user import UserBaseMinimum


class AppointmentResponse(BaseModel):
    id: int
    start_date: datetime
    end_date: datetime
    status: str
    instant_booking: bool
    channel: str
    exchange_rate: int
    is_blocked: bool
    user_id: int
    business_id: int
    service_id: int
    currency_id: int
    product_id: Optional[int] = None
    customer_id: Optional[int] = None
    message: Optional[str] = None
    customer_fullname: str = Field(min_length=3, max_length=50)
    service_name: str
    product_name: str = Field(min_length=3, max_length=100)
    product_full_price: condecimal(gt=0, max_digits=10, decimal_places=2)
    product_price_with_discount: condecimal(gt=0, max_digits=10, decimal_places=2)
    product_discount: condecimal(max_digits=10, decimal_places=2)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AppointmentCreateOwnClient(BaseModel):
    start_date: datetime
    end_date: datetime
    user_id: int
    business_id: int
    currency_id: int
    service_id: int
    product_id: Optional[int] = None
    customer_fullname: str = Field(min_length=3, max_length=50)
    service_name: str= Field(min_length=3, max_length=50)
    product_name: str = Field(min_length=3, max_length=100)
    product_full_price: condecimal(gt=0, max_digits=10, decimal_places=2)
    product_price_with_discount: condecimal(gt=0, max_digits=10, decimal_places=2)
    product_discount: condecimal(max_digits=10, decimal_places=2)

class AppointmentCancel(BaseModel):
    appointment_id: int
    message: str = Field(min_length=3, max_length=50)

class AppointmentBlock(BaseModel):
    message: str = Field(min_length=3, max_length=50)
    start_date: datetime
    end_date: datetime
    user_id: int

class AppointmentUnblock(BaseModel):
    start_date: datetime
    end_date:datetime

class AppointmentTimeslot(BaseModel):
    start_date_utc: str
    end_date_utc: str
    start_date_locale: str
    end_date_locale: str

class AppointmentTimeslotsResponse(BaseModel):
    is_closed: bool
    available_slots: list[AppointmentTimeslot]

class AppointmentUser(BaseModel):
    id: Optional[int] = None
    fullname: str
    username: Optional[str] = None
    avatar: Optional[str] = None
    profession: Optional[str] = None

class AppointmentProduct(BaseModel):
    id: Optional[int] = None
    name: str
    price: condecimal(gt=0, max_digits=10, decimal_places=2)
    price_with_discount: condecimal(gt=0, max_digits=10, decimal_places=2)
    discount: condecimal(max_digits=10, decimal_places=2)
    currency: str

class UserAppointmentResponse(BaseModel):
    id: int
    start_date: str
    end_date: str
    channel: str
    status: str
    product: AppointmentProduct
    user: UserBaseMinimum