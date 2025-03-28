from fastapi import APIRouter
from starlette.requests import Request
from app.schema.booking.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from app.service.booking.schedule import create_user_schedule, update_user_schedule
from app.core.dependencies import DBSession, BusinessAndEmployeesSession

router = APIRouter(prefix="/businesses/{business_id}/schedules", tags=["Schedules"])

@router.post("/", response_model=ScheduleResponse, dependencies=[BusinessAndEmployeesSession])
async def create_schedule(db: DBSession, business_id: int, schedule_update: ScheduleCreate, request: Request):
    return await create_user_schedule(db, business_id, schedule_update, request)

@router.put("/{schedule_id}", dependencies=[BusinessAndEmployeesSession])
async def update_schedule(db: DBSession, business_id: int, schedule_id: int, schedule_update: ScheduleUpdate, request: Request):
    return await update_user_schedule(db, business_id, schedule_id, schedule_update, request)