from fastapi import APIRouter
from starlette.requests import Request
from app.core.dependencies import DBSession, BusinessSession, ClientSession
from app.service.booking.employment_request import send_employment_request, accept_employment_request
from app.schema.booking.employment_request import EmploymentRequestResponse, EmploymentRequestCreate, EmploymentRequestUpdate

router = APIRouter(prefix="/employment-requests", tags=["Employment Request"])

@router.post("/", response_model=EmploymentRequestResponse, dependencies=[BusinessSession])
async def create_request(db: DBSession, new_employment: EmploymentRequestCreate, request: Request):
    return await send_employment_request(db, new_employment, request)

@router.put("/{employment_request_id}", dependencies=[ClientSession])
async def accept_request(db: DBSession, employment_request_id: int, employment_update: EmploymentRequestUpdate,  request: Request):
    return await accept_employment_request(db, employment_request_id, employment_update, request)