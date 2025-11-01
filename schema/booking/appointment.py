from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

from core.enums.appointment_channel_enum import AppointmentChannelEnum
from core.enums.appointment_status_enum import AppointmentStatusEnum
from schema.booking.business import BusinessCoordinates
from schema.nomenclature.currency import CurrencyMiniResponse

class AppointmentBusiness(BaseModel):
    address: str
    coordinates: BusinessCoordinates
    map_url: Optional[str] = None

class AppointmentUser(BaseModel):
    id: Optional[int] = None
    fullname: str
    username: Optional[str] = None
    avatar: Optional[str] = None
    profession: Optional[str] = None

class AppointmentProductResponse(BaseModel):
    id: Optional[int] = None
    name: str
    price: Decimal
    price_with_discount: Decimal
    discount: Decimal
    duration: int
    currency: CurrencyMiniResponse
    converted_price_with_discount: Decimal
    exchange_rate: Optional[Decimal] = None

class AppointmentResponse(BaseModel):
    id: int
    start_date: datetime
    end_date: datetime
    channel: str
    status: str
    message: Optional[str] = None
    is_customer: bool
    products: List[AppointmentProductResponse]
    user: AppointmentUser
    customer: AppointmentUser
    business: AppointmentBusiness
    total_price: Decimal
    total_duration: int
    payment_currency: CurrencyMiniResponse

class AppointmentScrollBookerCreate(BaseModel):
    start_date: datetime
    end_date: datetime
    user_id: int
    product_ids: List[int]
    payment_currency_id: int

    @field_validator("product_ids")
    @classmethod
    def unique_product_ids(cls, v: List[int]):
        if len(v) != len(set(v)):
            same_ids = sorted({x for x in v if v.count(x) > 1})
            raise ValueError(f"product_ids has same ids: {sorted(set(same_ids))}")
        return v

class AppointmentOwnClientCreate(BaseModel):
    start_date: datetime
    end_date: datetime
    customer_fullname: str = Field(min_length=3, max_length=50)
    service_name: str = Field(min_length=3, max_length=50)

    product_name: str = Field(min_length=3, max_length=100)
    product_full_price: Decimal
    product_price_with_discount: Decimal
    product_discount: Decimal
    product_duration: int

    service_id: Optional[int] = None
    product_id: Optional[int] = None
    currency_id: int
    channel: AppointmentStatusEnum = AppointmentChannelEnum.OWN_CLIENT

class AppointmentBlockSlot(BaseModel):
    start_date: datetime
    end_date: datetime

    customer_fullname: str = "Blocked"
    service_name: str = "Blocked"
    product_name: str = "Blocked"
    product_full_price: Decimal = Decimal("0.00")
    product_price_with_discount: Decimal = Decimal("0.00")
    product_duration: Decimal = Decimal("0.00")
    product_discount: Decimal = Decimal("0.00")
    is_blocked: bool = True
    status: AppointmentStatusEnum = AppointmentStatusEnum.FINISHED
    channel: AppointmentStatusEnum = AppointmentChannelEnum.OWN_CLIENT

class AppointmentBlock(BaseModel):
    message: str = Field(min_length=3, max_length=50)
    slots: List[AppointmentBlockSlot]

class AppointmentCancel(BaseModel):
    appointment_id: int
    message: str = Field(min_length=3, max_length=50)

class AppointmentTimeslot(BaseModel):
    start_date_utc: str
    end_date_utc: str
    start_date_locale: str
    end_date_locale: str

class AppointmentTimeslotsResponse(BaseModel):
    is_closed: bool
    available_slots: list[AppointmentTimeslot]

class CalendarEventsProduct(BaseModel):
    product_name: str
    product_full_price: Decimal
    product_price_with_discount: Decimal
    product_discount: Decimal

class CalendarEventsCustomer(BaseModel):
    id: Optional[int] = None
    fullname: str
    username: Optional[str] = None
    avatar: Optional[str] = None

class CalendarEventsInfo(BaseModel):
    currency: Optional[CurrencyMiniResponse] = None
    channel: str
    service_name: str
    product: CalendarEventsProduct
    customer: Optional[CalendarEventsCustomer] = None
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