from typing import List

from fastapi import APIRouter, Request, status, Query

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, BusinessAndEmployeesSession, Pagination, AuthenticatedUser
from service.booking.product import create_new_product, delete_by_id, update_by_id, get_products_by_user_id, \
    get_products_by_user_id_and_service_id, get_product_by_id, get_products_by_appointment_id, get_products_by_post_id
from schema.booking.product import ProductResponse, ProductCreateWithSubFilters, ProductUpdate, ProductWithSubFiltersResponse

router = APIRouter(tags=["Products"])

@router.get(
    "/users/{user_id}/products",
    summary="List All Products Filtered By User Id",
    response_model=PaginatedResponse[ProductWithSubFiltersResponse])
async def get_products_by_user(
        db: DBSession,
        user_id: int,
        pagination: Pagination
) -> PaginatedResponse[ProductWithSubFiltersResponse]:
    return await get_products_by_user_id(db, user_id, pagination)

@router.get(
    "/users/{user_id}/services/{service_id}/products",
    summary="List All Products Filtered By User Id and Service Id",
    response_model=PaginatedResponse[ProductResponse])
async def get_products_by_user_and_service(
        db: DBSession,
        user_id: int,
        service_id: int,
        pagination: Pagination,
        employee_id: int = Query(None),
) -> PaginatedResponse[ProductResponse]:
    return await get_products_by_user_id_and_service_id(db, user_id, service_id, pagination, employee_id)

@router.get("/products/{product_id}",
    summary='Get Product By Id',
    response_model=ProductResponse)
async def get_product(db: DBSession, product_id: int) -> ProductResponse:
    return await get_product_by_id(db, product_id)

@router.get("/appointments/{appointment_id}/products",
            summary='List All Products Filtered By Appointment Id',
            response_model=List[ProductResponse])
async def get_products_by_appointment(db: DBSession, appointment_id: int) -> List[ProductResponse]:
    return await get_products_by_appointment_id(db, appointment_id)

@router.get("/posts/{post_id}/products",
            summary='List All Products Filtered By Post Id',
            response_model=List[ProductResponse])
async def get_products_by_post(db: DBSession, post_id: int) -> List[ProductResponse]:
    return await get_products_by_post_id(db, post_id)

@router.post(
    "/products",
    summary="Create New Product",
    response_model=ProductResponse,
    dependencies=[BusinessAndEmployeesSession])
async def create_product(
        db: DBSession,
        product_with_sub_filters: ProductCreateWithSubFilters,
        auth_user: AuthenticatedUser
) -> ProductResponse:
    return await create_new_product(db, product_with_sub_filters, auth_user)

@router.put(
    "/products/{product_id}",
    summary="Update Product",
    response_model=ProductResponse,
    dependencies=[BusinessAndEmployeesSession])
async def update_product(
        db: DBSession,
        product_id: int,
        product_update: ProductUpdate,
        auth_user: AuthenticatedUser
) -> ProductResponse:
    return await update_by_id(db, product_id, product_update, auth_user)

@router.delete(
    "/products/{product_id}",
    summary="Delete Product",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[BusinessAndEmployeesSession])
async def delete_product(db: DBSession, product_id: int, auth_user: AuthenticatedUser):
    return await delete_by_id(db, product_id, auth_user)

