from typing import List

from fastapi import APIRouter, Request
from schema.booking.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from service.booking.schedule import create_user_schedule, update_user_schedules, get_schedules_by_user_id
from core.dependencies import DBSession, BusinessAndEmployeesSession, AuthenticatedUser

router = APIRouter(tags=["Schedules"])

@router.get(
    "/users/{user_id}/schedules",
    summary='List All Schedules Filtered By User Id',
    response_model=List[ScheduleResponse])
async def get_user_schedules(db: DBSession, user_id: int):
    return await get_schedules_by_user_id(db, user_id)

@router.post(
    "/schedules",
    summary='Create New Schedule',
    response_model=ScheduleResponse,
    dependencies=[BusinessAndEmployeesSession])
async def create_schedule(
        db: DBSession,
        schedule_update: ScheduleCreate,
        auth_user: AuthenticatedUser
) -> ScheduleResponse:
    return await create_user_schedule(db, schedule_update, auth_user)

@router.put(
    "/schedules",
    summary='Update Many Schedules',
    response_model=List[ScheduleResponse],
    dependencies=[BusinessAndEmployeesSession])
async def update_many_schedules(
        db: DBSession,
        schedule_update: List[ScheduleUpdate],
        auth_user: AuthenticatedUser
) -> List[ScheduleResponse]:
    return await update_user_schedules(db, schedule_update, auth_user)