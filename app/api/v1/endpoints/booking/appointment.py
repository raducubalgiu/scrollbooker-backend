from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from app.core.dependencies import DBSession, BusinessAndEmployeesSession
from app.schema.booking.appointment import AppointmentResponse, AppointmentBlock, \
    AppointmentCancel, AppointmentTimeslotsResponse, AppointmentUnblock, AppointmentCreateOwnClient
from app.service.booking.appointment import create_new_appointment_own_client, get_daily_available_slots, \
    get_user_calendar_events, create_new_blocked_appointment, get_user_calendar_availability, cancel_user_appointment, \
    unblock_user_appointment

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/create-own-client", response_model=AppointmentResponse, dependencies=[BusinessAndEmployeesSession])
async def create_appointment_own_client(db: DBSession, appointment_create: AppointmentCreateOwnClient, request: Request):
    return await create_new_appointment_own_client(db, appointment_create, request)

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
async def get_calendar_available_days(db: DBSession, month: str, user_id: int):
    return await get_user_calendar_availability(db, month, user_id)

@router.get("/calendar-events")
async def get_calendar_events(db: DBSession, start_date: str, end_date: str, user_id: int, slot_duration: int):
    return await get_user_calendar_events(db, start_date, end_date, user_id, slot_duration)