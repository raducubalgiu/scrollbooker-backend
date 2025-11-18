from typing import Optional, List

from fastapi import APIRouter, Response, Request, status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, BusinessAndEmployeesSession, ClientAndEmployeeSession, AuthenticatedUser, \
    Pagination
from schema.booking.appointment import AppointmentBlock, \
    AppointmentCancel, AppointmentTimeslotsResponse, AppointmentScrollBookerCreate, AppointmentResponse, \
    CalendarEventsResponse, AppointmentOwnClientCreate
from service.booking.apppointment.create_update_appointments import create_new_scroll_booker_appointment, create_new_blocked_appointment, cancel_user_appointment, create_new_own_client_appointment
from service.booking.apppointment.get_appointments import get_appointments_by_user_id, \
    get_appointments_number_by_user_id, get_daily_available_slots, get_user_calendar_availability, \
    get_user_calendar_events, get_appointment_by_id

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/create-scrollbooker-appointment",
            summary='Create New Appointment - Client & Employee',
            #response_model=AppointmentResponse,
            dependencies=[ClientAndEmployeeSession])
async def create_scroll_booker_appointment(
        db: DBSession,
        appointment_create: AppointmentScrollBookerCreate,
        auth_user: AuthenticatedUser
):
    return await create_new_scroll_booker_appointment(db, appointment_create, auth_user)

@router.post("/create-own-client-appointment",
            summary='Create New Appointment - Client & Employee',
            response_model=AppointmentResponse,
            dependencies=[BusinessAndEmployeesSession])
async def create_own_client_appointment(
        db: DBSession,
        appointment_create: AppointmentOwnClientCreate,
        auth_user: AuthenticatedUser
):
    return await create_new_own_client_appointment(db, appointment_create, auth_user)

@router.post("/create-block-appointments",
             summary='Create Block Appointments - Business & Employees',
             status_code=status.HTTP_201_CREATED,
             dependencies=[BusinessAndEmployeesSession])
async def create_blocked_appointment(
        db: DBSession,
        appointments_create: AppointmentBlock,
        auth_user: AuthenticatedUser
):
    return await create_new_blocked_appointment(db, appointments_create, auth_user)

@router.put("/cancel-appointment",
            summary='Cancel Appointment',
            status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
        db: DBSession,
        appointment_cancel: AppointmentCancel,
        auth_user: AuthenticatedUser
) -> Response:
    return await cancel_user_appointment(db, appointment_cancel, auth_user)

@router.get("/",
            summary='List All Appointments Filtered By User',
            response_model=PaginatedResponse[AppointmentResponse])
async def get_appointments_by_user(
        db: DBSession,
        pagination: Pagination,
        auth_user: AuthenticatedUser,
        as_customer: Optional[bool] = None
):
    return await get_appointments_by_user_id(db, pagination, auth_user, as_customer)

@router.get("/count",
            summary='Get User Appointments Number',
            response_model=int)
async def get_appointment_number_by_user(db: DBSession, auth_user: AuthenticatedUser) -> int:
    return await get_appointments_number_by_user_id(db, auth_user)

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

@router.get("/{appointment_id}",
            summary='Get Appointment By Id')
async def get_appointment(db: DBSession, appointment_id: int, request: Request):
    return await get_appointment_by_id(db, appointment_id, request)