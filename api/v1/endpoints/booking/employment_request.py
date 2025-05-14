from fastapi import APIRouter
from starlette.requests import Request
from starlette import status
from backend.core.dependencies import DBSession, BusinessSession, ClientSession, BusinessAndEmployeesSession
from backend.service.booking.employment_request import send_employment_request, accept_employment_request, \
    delete_employment_request_by_id, get_employment_requests_by_user_id
from backend.schema.booking.employment_request import EmploymentRequestCreate, EmploymentRequestUpdate, \
    EmploymentRequestResponse

router = APIRouter(tags=["Employment Request"])

@router.get(
    "/users/{user_id}/employment-requests",
    summary="List Employment Requests Filtered By User Id",
    response_model=list[EmploymentRequestResponse])
async def get_user_employment_requests(db: DBSession, user_id: int, request: Request):
    return await get_employment_requests_by_user_id(db, user_id, request)

@router.post(
    "/employment-requests",
    summary="Create New Employment Request",
    status_code=status.HTTP_201_CREATED,
    dependencies=[BusinessSession])
async def create_request(db: DBSession, employment_create: EmploymentRequestCreate, request: Request):
    return await send_employment_request(db, employment_create, request)

@router.put(
    "/employment-requests/{employment_request_id}",
    summary="Accept Employment Request",
    dependencies=[ClientSession])
async def accept_request(db: DBSession, employment_request_id: int, employment_update: EmploymentRequestUpdate,  request: Request):
    return await accept_employment_request(db, employment_request_id, employment_update, request)

@router.delete(
    "/employment-requests/{employment_request_id}",
    summary="Cancel Employment Request",
    dependencies=[BusinessAndEmployeesSession])
async def delete_request(db: DBSession, employment_request_id: int, request: Request):
    return await delete_employment_request_by_id(db, employment_request_id, request)