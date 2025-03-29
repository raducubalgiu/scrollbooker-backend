from fastapi import APIRouter
from starlette import status

from app.core.crud_helpers import PaginatedResponse
from app.core.dependencies import DBSession
from app.core.dependencies import SuperAdminSession
from app.schema.booking.nomenclature.service import ServiceResponse, ServiceCreate, ServiceUpdate
from app.service.booking.nomenclature.service import create_new_service, \
    delete_service_by_id, update_service_by_id, get_all_services, attach_services_to_business_type, \
    detach_services_from_business_type

router = APIRouter(prefix="/services", tags=["Services"])

@router.get("/", response_model=PaginatedResponse[ServiceResponse])
async def get_services(db: DBSession, page: int, limit: int):
    return await get_all_services(db, page, limit)

@router.post("/", response_model=ServiceResponse, dependencies=[SuperAdminSession])
async def create_service(db: DBSession, new_service: ServiceCreate):
    return await create_new_service(db, new_service)

@router.put("/{service_id}", response_model=ServiceResponse, dependencies=[SuperAdminSession])
async def update_service(db: DBSession, service_id: int, service_data: ServiceUpdate):
    return await update_service_by_id(db, service_id, service_data)

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[SuperAdminSession])
async def delete_service(db: DBSession, service_id: int):
    return await delete_service_by_id(db, service_id)

@router.post("/{service_id}/business-types/{business_type_id}", status_code=status.HTTP_201_CREATED)
async def attach_service_business_type(db: DBSession, service_id: int, business_type_id: int):
    return await attach_services_to_business_type(db, business_type_id, service_id)

@router.delete("/{service_id}/business-types/{business_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def detach_service_business_type(db: DBSession, service_id: int, business_type_id: int):
    return await detach_services_from_business_type(db, business_type_id, service_id)