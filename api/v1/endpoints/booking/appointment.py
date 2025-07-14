from typing import Optional

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, BusinessAndEmployeesSession
from schema.booking.appointment import AppointmentResponse, AppointmentBlock, \
    AppointmentCancel, AppointmentTimeslotsResponse, AppointmentUnblock, AppointmentCreate, UserAppointmentResponse
from service.booking.appointment import create_new_appointment, get_daily_available_slots, \
    get_user_calendar_events, create_new_blocked_appointment, get_user_calendar_availability, cancel_user_appointment, \
    unblock_user_appointment, get_appointments_by_user_id, get_appointments_number_by_user_id

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.get("/",
            summary='List All Appointments Filtered By User',
            response_model=PaginatedResponse[UserAppointmentResponse])
async def get_appointments_by_user(db: DBSession, page: int, limit: int, request: Request, as_customer: Optional[bool] = None):
    return await get_appointments_by_user_id(db, page, limit, request, as_customer)

@router.get("/count",
            summary='Get User Appointments Number')
async def get_appointment_number_by_user(db: DBSession, request: Request):
    return await get_appointments_number_by_user_id(db, request)

@router.post("/")
async def create_appointment(db: DBSession, appointment_create: AppointmentCreate, request: Request):
    return await create_new_appointment(db, appointment_create, request)

@router.post("/block-appointments", status_code=status.HTTP_201_CREATED, dependencies=[BusinessAndEmployeesSession])
async def create_blocked_appointment(db: DBSession, appointments_create: list[AppointmentBlock], request: Request):
    return await create_new_blocked_appointment(db, appointments_create, request)

@router.post("/unblock-appointment", status_code=status.HTTP_204_NO_CONTENT, dependencies=[BusinessAndEmployeesSession])
async def unblock_appointment(db: DBSession, appointment_unblock: AppointmentUnblock, request: Request):
    return await unblock_user_appointment(db, appointment_unblock, request)

@router.put("/cancel-appointment", response_model=AppointmentResponse)
async def cancel_appointment(db: DBSession, appointment_cancel: AppointmentCancel, request: Request):
    return await cancel_user_appointment(db, appointment_cancel, request)

@router.get("/timeslots", response_model=AppointmentTimeslotsResponse)
async def get_daily_timeslots(db: DBSession, day: str, user_id: int, slot_duration: int):
    return await get_daily_available_slots(db, day, user_id, slot_duration)

@router.get("/calendar-available-days", response_model=list[str])
async def get_calendar_available_days(db: DBSession, start_date: str, end_date: str, user_id: int):
    return await get_user_calendar_availability(db, start_date, end_date, user_id)

@router.get("/calendar-events")
async def get_calendar_events(db: DBSession, start_date: str, end_date: str, user_id: int, slot_duration: int):
    return await get_user_calendar_events(db, start_date, end_date, user_id, slot_duration)