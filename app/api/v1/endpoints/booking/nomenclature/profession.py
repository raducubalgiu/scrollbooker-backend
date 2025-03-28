from fastapi import APIRouter
from starlette import status
from app.core.dependencies import DBSession, SuperAdminSession
from app.schema.booking.nomenclature.profession import ProfessionCreate, ProfessionResponse, ProfessionUpdate
from app.service.booking.nomenclature.profession import create_new_profession, \
    update_profession_by_id, delete_profession_by_id, get_all_professions_with_business_types

router = APIRouter(prefix="/professions", tags=["Professions"])

@router.get("/")
async def get_professions_with_business_types(db: DBSession, page: int, limit: int):
    return await get_all_professions_with_business_types(db, page, limit)

@router.post("/", response_model=ProfessionResponse, dependencies=[SuperAdminSession])
async def create_profession(db: DBSession, profession_create: ProfessionCreate):
    return await create_new_profession(db, profession_create)

@router.put("/{profession_id}", response_model=ProfessionResponse, dependencies=[SuperAdminSession])
async def update_profession(db: DBSession, profession_update: ProfessionUpdate, profession_id: int):
    return await update_profession_by_id(db, profession_update, profession_id)

@router.delete("/{profession_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[SuperAdminSession])
async def delete_profession(db:DBSession, profession_id: int):
    return await delete_profession_by_id(db, profession_id)