from typing import Optional, List

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, BusinessAndEmployeesSession, ClientAndEmployeeSession
from schema.booking.appointment import AppointmentResponse, AppointmentBlock, \
    AppointmentCancel, AppointmentTimeslotsResponse, AppointmentScrollBookerCreate, UserAppointmentResponse, \
    CalendarEventsResponse, AppointmentOwnClientCreate
from service.booking.appointment import create_new_scroll_booker_appointment, get_daily_available_slots, \
    get_user_calendar_events, create_new_blocked_appointment, get_user_calendar_availability, cancel_user_appointment, \
    get_appointments_by_user_id, get_appointments_number_by_user_id, create_new_own_client_appointment

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.get("/",
            summary='List All Appointments Filtered By User',
            response_model=PaginatedResponse[UserAppointmentResponse])
async def get_appointments_by_user(db: DBSession, page: int, limit: int, request: Request, as_customer: Optional[bool] = None):
    return await get_appointments_by_user_id(db, page, limit, request, as_customer)

@router.get("/count",
            summary='Get User Appointments Number',
            response_model=int)
async def get_appointment_number_by_user(db: DBSession, request: Request):
    return await get_appointments_number_by_user_id(db, request)

@router.post("/create-scrollbooker-appointment",
            summary='Create New Appointment - Client & Employee',
            response_model=AppointmentResponse,
            dependencies=[ClientAndEmployeeSession])
async def create_scroll_booker_appointment(
        db: DBSession,
        appointment_create: AppointmentScrollBookerCreate,
        request: Request
):
    return await create_new_scroll_booker_appointment(db, appointment_create, request)

@router.post("/create-own-client-appointment",
            summary='Create New Appointment - Client & Employee',
            response_model=AppointmentResponse,
            dependencies=[BusinessAndEmployeesSession])
async def create_own_client_appointment(
        db: DBSession,
        appointment_create: AppointmentOwnClientCreate,
        request: Request
):
    return await create_new_own_client_appointment(db, appointment_create, request)

@router.post("/create-block-appointments",
             summary='Create Block Appointments - Business & Employees',
             status_code=status.HTTP_201_CREATED,
             dependencies=[BusinessAndEmployeesSession])
async def create_blocked_appointment(db: DBSession, appointments_create: AppointmentBlock, request: Request):
    return await create_new_blocked_appointment(db, appointments_create, request)

@router.put("/cancel-appointment",
            summary='Cancel Appointment',
            response_model=AppointmentResponse)
async def cancel_appointment(db: DBSession, appointment_cancel: AppointmentCancel, request: Request):
    return await cancel_user_appointment(db, appointment_cancel, request)

@router.get("/timeslots",
            summary='Get User daily available timeslots',
            response_model=AppointmentTimeslotsResponse)
async def get_daily_timeslots(db: DBSession, day: str, user_id: int, slot_duration: int):
    return await get_daily_available_slots(db, day, user_id, slot_duration)

@router.get("/calendar-available-days",
            summary='Get User available days',
            response_model=List[str])
async def get_calendar_available_days(db: DBSession, start_date: str, end_date: str, user_id: int):
    return await get_user_calendar_availability(db, start_date, end_date, user_id)

@router.get("/calendar-events",
            summary='Get Business/Employee Calendar Events',
            response_model=CalendarEventsResponse,
            dependencies=[BusinessAndEmployeesSession])
async def get_calendar_events(db: DBSession, start_date: str, end_date: str, user_id: int, slot_duration: int):
    return await get_user_calendar_events(db, start_date, end_date, user_id, slot_duration)