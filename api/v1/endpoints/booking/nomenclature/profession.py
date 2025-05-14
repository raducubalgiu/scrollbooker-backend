from fastapi import APIRouter
from starlette import status

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession, SuperAdminSession
from backend.schema.booking.nomenclature.profession import ProfessionCreate, ProfessionResponse, ProfessionUpdate, \
    ProfessionWithBusinessTypesResponse
from backend.service.booking.nomenclature.profession import create_new_profession, \
    update_profession_by_id, delete_profession_by_id, get_all_professions_with_business_types, get_professions_by_business_type_id

router = APIRouter(tags=["Professions"])

@router.get(
    "/business-types/{business_type_id}/professions",
    summary='List All Professions Filtered By Business Id',
    response_model=list[ProfessionResponse])
async def get_professions_by_business_type(db: DBSession, business_type_id: int):
    return await get_professions_by_business_type_id(db, business_type_id)

@router.get(
    "/professions/with-business-types",
    summary='List All Professions with Business Types',
    response_model=PaginatedResponse[ProfessionWithBusinessTypesResponse])
async def get_professions_with_business_types(db: DBSession, page: int, limit: int):
    return await get_all_professions_with_business_types(db, page, limit)

@router.post(
    "/professions",
    summary='Create New Profession',
    response_model=ProfessionResponse,
    dependencies=[SuperAdminSession])
async def create_profession(db: DBSession, profession_create: ProfessionCreate):
    return await create_new_profession(db, profession_create)

@router.put(
    "/professions/{profession_id}",
    summary='Update Profession',
    response_model=ProfessionResponse,
    dependencies=[SuperAdminSession])
async def update_profession(db: DBSession, profession_update: ProfessionUpdate, profession_id: int):
    return await update_profession_by_id(db, profession_update, profession_id)

@router.delete(
    "/professions/{profession_id}",
    summary='Delete Profession',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def delete_profession(db:DBSession, profession_id: int):
    return await delete_profession_by_id(db, profession_id)