from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, condecimal, Field, field_serializer
from datetime import datetime

from core.enums.appointment_channel_enum import AppointmentChannelEnum
from schema.booking.business import BusinessCoordinates
from schema.nomenclature.currency import CurrencyMiniResponse
from schema.user.user import UserBaseMinimum

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

class AppointmentCreate(BaseModel):
    start_date: datetime
    end_date: datetime
    user_id: int
    business_id: int
    customer_id: Optional[int] = None
    currency_id: int
    service_id: int

    product_id: Optional[int] = None
    product_name: str = Field(min_length=3, max_length=100)
    product_full_price: Decimal
    product_price_with_discount: Decimal
    product_duration: int
    product_discount: Decimal

    channel: AppointmentChannelEnum
    customer_fullname: str = Field(min_length=3, max_length=50)

class AppointmentCancel(BaseModel):
    appointment_id: int
    message: str = Field(min_length=3, max_length=50)

class AppointmentBlockSlot(BaseModel):
    start_date: datetime
    end_date: datetime

class AppointmentBlock(BaseModel):
    message: str = Field(min_length=3, max_length=50)
    user_id: int
    slots: List[AppointmentBlockSlot]

class AppointmentTimeslot(BaseModel):
    start_date_utc: str
    end_date_utc: str
    start_date_locale: str
    end_date_locale: str

class AppointmentTimeslotsResponse(BaseModel):
    is_closed: bool
    available_slots: list[AppointmentTimeslot]

class AppointmentProduct(BaseModel):
    id: Optional[int] = None
    name: str
    price: Decimal
    price_with_discount: Decimal
    duration: int
    discount: Decimal
    currency: str
    exchange_rate: Decimal

    @field_serializer("price", "price_with_discount", "discount", return_type=str)
    def serialize_price(self, value: Decimal, _info) -> str:
        return '{0:.2f}'.format(value).rstrip('0').rstrip('.') if value is not None else None

class AppointmentBusiness(BaseModel):
    address: str
    coordinates: BusinessCoordinates

class UserAppointmentResponse(BaseModel):
    id: int
    start_date: datetime
    end_date: datetime
    channel: str
    status: str
    message: Optional[str] = None
    is_customer: bool
    product: AppointmentProduct
    user: UserBaseMinimum
    business: AppointmentBusiness

class CalendarEventsProduct(BaseModel):
    product_name: str
    product_full_price: Decimal
    product_price_with_discount: Decimal
    product_discount: Decimal

class CalendarEventsInfo(BaseModel):
    currency: Optional[CurrencyMiniResponse] = None
    channel: str
    service_name: str
    product: CalendarEventsProduct
    customer: Optional[UserBaseMinimum] = None
    message: Optional[str] = None

class CalendarEventsSlot(BaseModel):
    id: Optional[int] = None
    start_date_locale: str
    end_date_locale: str
    start_date_utc: str
    end_date_utc: str
    is_booked: bool
    is_closed: bool
    is_blocked: bool
    info: Optional[CalendarEventsInfo] = None

class CalendarEventsDay(BaseModel):
    day: str
    is_booked: bool
    is_closed: bool
    slots: List[CalendarEventsSlot]

class CalendarEventsResponse(BaseModel):
    min_slot_time: Optional[str] = None
    max_slot_time: Optional[str] = None
    days: List[CalendarEventsDay]