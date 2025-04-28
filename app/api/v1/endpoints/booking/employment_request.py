from fastapi import APIRouter
from starlette.requests import Request
from starlette import status
from app.core.dependencies import DBSession, BusinessSession, ClientSession, BusinessAndEmployeesSession
from app.service.booking.employment_request import send_employment_request, accept_employment_request, \
    delete_employment_request_by_id
from app.schema.booking.employment_request import EmploymentRequestCreate, EmploymentRequestUpdate

router = APIRouter(prefix="/employment-requests", tags=["Employment Request"])

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[BusinessSession])
async def create_request(db: DBSession, employment_create: EmploymentRequestCreate, request: Request):
    return await send_employment_request(db, employment_create, request)

@router.put("/{employment_request_id}", dependencies=[ClientSession])
async def accept_request(db: DBSession, employment_request_id: int, employment_update: EmploymentRequestUpdate,  request: Request):
    return await accept_employment_request(db, employment_request_id, employment_update, request)

@router.delete("/{employment_request_id}", dependencies=[BusinessAndEmployeesSession])
async def delete_request(db: DBSession, employment_request_id: int, request: Request):
    return await delete_employment_request_by_id(db, employment_request_id, request)