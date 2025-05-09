from fastapi import APIRouter
from starlette.requests import Request
from starlette import status
from app.core.dependencies import DBSession, BusinessAndEmployeesSession, Pagination
from app.service.booking.product import create_new_product, delete_by_id, update_by_id, get_by_user,get_by_user_and_service
from app.schema.booking.product import ProductResponse, ProductCreateWithSubFilters, ProductUpdate

router = APIRouter(tags=["Products"])

@router.get("/users/{user_id}/products")
async def get_products_by_user(db: DBSession, user_id: int, pagination: Pagination):
    return await get_by_user(db, user_id, pagination)

@router.get("/users/{user_id}/services/{service_id}/products", response_model=list[ProductResponse])
async def get_products_by_user_and_service(db: DBSession, user_id: int, service_id: int):
    return await get_by_user_and_service(db, user_id, service_id)

@router.post("/products", response_model=ProductResponse, dependencies=[BusinessAndEmployeesSession])
async def create_product(db: DBSession, product_with_sub_filters: ProductCreateWithSubFilters, request: Request):
    return await create_new_product(db, product_with_sub_filters, request)

@router.put("/products/{product_id}", response_model=ProductResponse, dependencies=[BusinessAndEmployeesSession])
async def update_product(db: DBSession, product_id: int, product_update: ProductUpdate, request: Request):
    return await update_by_id(db, product_id, product_update, request)

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[BusinessAndEmployeesSession])
async def delete_product(db: DBSession, product_id: int, request: Request):
    return await delete_by_id(db, product_id, request)

