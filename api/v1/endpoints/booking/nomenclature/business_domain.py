from typing import Union

from fastapi import APIRouter
from starlette import status

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, SuperAdminSession, Pagination
from backend.schema.booking.nomenclature.business_domain import BusinessDomainResponse, BusinessDomainCreate, BusinessDomainUpdate
from backend.service.booking.nomenclature.business_domain import create_new_business_domain, get_all_business_domain, update_business_domain_by_id, delete_business_domain_by_id

router = APIRouter(prefix="/business-domains", tags=["Businesses Domain"])

@router.get("/",
    summary='List All Business Domains',
    response_model=Union[PaginatedResponse[BusinessDomainResponse], list[BusinessDomainResponse]])
async def get_business_domain(db: DBSession, pagination: Pagination):
    return await get_all_business_domain(db, pagination)

@router.post("/",
    summary='Create New Business Domain',
    response_model=BusinessDomainResponse,
    dependencies=[SuperAdminSession])
async def create_business_domain(db: DBSession, business_domain_create: BusinessDomainCreate):
    return await create_new_business_domain(db, business_domain_create)

@router.put("/{business_domain_id}",
    response_model=BusinessDomainResponse,
    summary='Update Business Domain',
    dependencies=[SuperAdminSession])
async def update_business_domain(db: DBSession, business_domain_update: BusinessDomainUpdate, business_domain_id: int):
    return await update_business_domain_by_id(db, business_domain_update, business_domain_id)

@router.delete("/{business_domain_id}",
    summary='Delete Business Domain',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def delete_business_domain(db: DBSession, business_domain_id: int):
    return await delete_business_domain_by_id(db, business_domain_id)