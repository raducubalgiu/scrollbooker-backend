from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from app.core.dependencies import DBSession
from app.schema.booking.appointment import AppointmentResponse, AppointmentCreate, AppointmentBlockedCreate
from app.service.booking.appointment import create_new_appointment, change_appointment_status, \
    get_daily_available_slots, \
    get_user_calendar_events, create_new_blocked_appointment, get_user_calendar_availability

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/block-appointments", status_code=status.HTTP_201_CREATED)
async def create_blocked_appointment(db: DBSession, appointments_create: list[AppointmentBlockedCreate], request: Request):
    return await create_new_blocked_appointment(db, appointments_create, request)

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(db: DBSession, appointment_create: AppointmentCreate, request: Request):
    return await create_new_appointment(db, appointment_create, request)

@router.put("/{appointment_id}/change-status", response_model=AppointmentResponse)
async def change_status(db: DBSession, appointment_id: int, status: str, request: Request):
    return await change_appointment_status(db, appointment_id, status, request)

@router.get("/timeslots", status_code=status.HTTP_200_OK)
async def get_daily_timeslots(db: DBSession, day: str, user_id: int, slot_duration: int):
    return await get_daily_available_slots(db, day, user_id, slot_duration)

@router.get("/calendar-available-days")
async def get_calendar_available_days(db: DBSession, month: str, user_id: int):
    return await get_user_calendar_availability(db, month, user_id)

@router.get("/calendar-events", status_code=status.HTTP_200_OK)
async def get_calendar_events(db: DBSession, start_date: str, end_date: str, user_id: int, slot_duration: int):
    return await get_user_calendar_events(db, start_date, end_date, user_id, slot_duration)