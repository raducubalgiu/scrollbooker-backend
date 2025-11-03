from typing import Union

from fastapi import APIRouter
from starlette import status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, SuperAdminSession, Pagination
from schema.nomenclature.profession import ProfessionCreate, ProfessionResponse, ProfessionUpdate, \
    ProfessionWithBusinessTypesResponse
from service.nomenclature.profession import create_new_profession, \
    update_profession_by_id, delete_profession_by_id, get_all_professions_with_business_types, \
    get_professions_by_business_type_id, get_all_professions, attach_professions_to_business_type, \
    detach_professions_from_business_type

router = APIRouter(tags=["Professions"])

@router.get("/business-types/{business_type_id}/professions",
    summary='List All Professions Filtered By Business Type Id',
    response_model=list[ProfessionResponse])
async def get_professions_by_business_type(db: DBSession, business_type_id: int):
    return await get_professions_by_business_type_id(db, business_type_id)

@router.get("/professions/with-business-types",
    summary='List All Professions with Business Types',
    response_model=PaginatedResponse[ProfessionWithBusinessTypesResponse])
async def get_professions_with_business_types(db: DBSession, pagination: Pagination):
    return await get_all_professions_with_business_types(db, pagination)

@router.get("/professions",
    summary='List All Professions',
    response_model=Union[PaginatedResponse[ProfessionResponse], list[ProfessionResponse]])
async def get_professions(db: DBSession, pagination: Pagination):
    return await get_all_professions(db, pagination)

@router.post("/professions",
    summary='Create New Profession',
    response_model=ProfessionResponse,
    dependencies=[SuperAdminSession])
async def create_profession(db: DBSession, profession_create: ProfessionCreate):
    return await create_new_profession(db, profession_create)

@router.put("/professions/{profession_id}",
    summary='Update Profession',
    response_model=ProfessionResponse,
    dependencies=[SuperAdminSession])
async def update_profession(db: DBSession, profession_update: ProfessionUpdate, profession_id: int):
    return await update_profession_by_id(db, profession_update, profession_id)

@router.delete("/professions/{profession_id}",
    summary='Delete Profession',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def delete_profession(db:DBSession, profession_id: int):
    return await delete_profession_by_id(db, profession_id)

@router.post("/professions/{profession_id}/business-types/{business_type_id}",
    summary='Attach Profession - Business Type',
    status_code=status.HTTP_201_CREATED,
    dependencies=[SuperAdminSession])
async def attach_professions_business_type(db: DBSession, business_type_id: int, profession_id: int):
    return await attach_professions_to_business_type(db, business_type_id, profession_id)

@router.delete("/professions/{profession_id}/business-types/{business_type_id}",
    summary='Detach Profession - Business Type',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def detach_professions_business_type(db:DBSession, business_type_id: int, profession_id: int):
    return await detach_professions_from_business_type(db, business_type_id, profession_id)
