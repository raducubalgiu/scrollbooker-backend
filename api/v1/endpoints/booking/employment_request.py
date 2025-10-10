from fastapi import APIRouter, Request, status

from core.dependencies import DBSession, BusinessSession, BusinessAndManagerSession, ClientAndBusinessSession
from service.booking.employment_request import get_employment_requests_by_user_id, \
    respond_employment_request, create_employment_request, get_employment_request_by_id
from schema.booking.employment_request import EmploymentRequestCreate, EmploymentRequestUpdate, EmploymentsRequestsResponse
router = APIRouter(tags=["Employment Request"])

@router.get("/users/{user_id}/employment-requests",
    summary="List Employment Requests Filtered By User Id",
    response_model=list[EmploymentsRequestsResponse],
    dependencies=[BusinessSession])
async def get_user_employment_requests(db: DBSession, user_id: int, request: Request):
    return await get_employment_requests_by_user_id(db, user_id, request)

@router.get("/employment-requests/{employment_id}",
            summary="Get Employment Request Details",
            response_model=EmploymentsRequestsResponse)
async def get_employment_request(db: DBSession, employment_id: int, request: Request):
    return await get_employment_request_by_id(db, employment_id, request)

@router.post(
    "/employment-requests",
    summary="Create New Employment Request",
    status_code=status.HTTP_201_CREATED,
    dependencies=[BusinessAndManagerSession])
async def create_employment(db: DBSession, employment_create: EmploymentRequestCreate, request: Request):
    return await create_employment_request(db, employment_create, request)

@router.put(
    "/employment-requests/{employment_request_id}",
    summary="Respond Employment Request",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[ClientAndBusinessSession])
async def respond_employment(db: DBSession, employment_request_id: int, employment_update: EmploymentRequestUpdate,  request: Request):
    return await respond_employment_request(db, employment_request_id, employment_update, request)