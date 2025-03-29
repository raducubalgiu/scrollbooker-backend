from fastapi import APIRouter
from app.core.dependencies import DBSession, SuperAdminSession
from app.schema.booking.nomenclature.filter import FilterResponse, FilterCreate, FilterUpdate, \
    FilterWithSubFiltersResponse
from app.service.booking.nomenclature.filter import create_new_filter, get_filters_with_sub_filters, update_filter_by_id

router = APIRouter(prefix="/filters", tags=["Filters"])

@router.get('/with-sub-filters', response_model=list[FilterWithSubFiltersResponse])
async def get_filters_sub_filters(db: DBSession):
    return await get_filters_with_sub_filters(db)

@router.post("/", response_model=FilterResponse, dependencies=[SuperAdminSession])
async def create_filter(db: DBSession, filter_create: FilterCreate):
    return await create_new_filter(db, filter_create)

@router.put("/{filter_id}", response_model=FilterResponse, dependencies=[SuperAdminSession])
async def update_filter(db: DBSession, filter_update: FilterUpdate, filter_id: int):
    return await update_filter_by_id(db, filter_update, filter_id)