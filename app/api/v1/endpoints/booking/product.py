from fastapi import APIRouter
from starlette.requests import Request
from starlette import status
from app.core.dependencies import DBSession, BusinessAndEmployeesSession
from app.service.booking.product import create_new_product, delete_product_by_id
from app.schema.booking.product import ProductResponse, ProductCreateWithSubFilters

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, dependencies=[BusinessAndEmployeesSession])
async def create_product(db: DBSession, product_with_sub_filters: ProductCreateWithSubFilters, request: Request):
    return await create_new_product(db, product_with_sub_filters, request)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[BusinessAndEmployeesSession])
async def delete_product_business(db: DBSession, product_id: int, request: Request):
    return await delete_product_by_id(db, product_id, request)

