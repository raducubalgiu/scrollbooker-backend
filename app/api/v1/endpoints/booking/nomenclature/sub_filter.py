from fastapi import APIRouter
from app.core.dependencies import DBSession, SuperAdminSession
from app.schema.booking.nomenclature.sub_filter import SubFilterCreate, SubFilterResponse, SubFilterUpdate
from app.service.booking.nomenclature.sub_filter import create_new_sub_filter, update_sub_filter_by_id

router = APIRouter(prefix="/sub-filters", tags=["SubFilters"])

@router.post("/", response_model=SubFilterResponse, dependencies=[SuperAdminSession])
async def create_sub_filter(db: DBSession, sub_filter_create: SubFilterCreate):
    return await create_new_sub_filter(db, sub_filter_create)

@router.put("/{sub_filter_id}", response_model=SubFilterResponse, dependencies=[SuperAdminSession])
async def update_sub_filter(db: DBSession, sub_filter_update: SubFilterUpdate, sub_filter_id: int):
    return await update_sub_filter_by_id(db, sub_filter_update, sub_filter_id)

