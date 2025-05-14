from fastapi import APIRouter
from starlette import status

from backend.core.crud_helpers import PaginatedResponse
from backend.core.dependencies import DBSession
from backend.schema.user.role import RoleResponse, RoleCreate, RoleUpdate
from backend.service.user.role import get_all_roles, create_new_role, delete_role_by_id, update_role_by_id

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get(
    "/",
    summary='List All Roles',
    response_model=PaginatedResponse[RoleResponse])
async def get_roles(db: DBSession, page: int, limit: int):
    return await get_all_roles(db, page, limit)

@router.post(
    "/",
    summary='Create New Role',
    response_model=RoleResponse)
async def create_role(db: DBSession, role_create: RoleCreate):
    return await create_new_role(db, role_create)

@router.put(
    "/{role_id}",
    summary='Update Role',
    response_model=RoleResponse)
async def update_role(db: DBSession, role_id: int, role_update: RoleUpdate):
    return await update_role_by_id(db, role_id, role_update)

@router.delete(
    "/{role_id}",
    summary='Delete Role',
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(db: DBSession, role_id: int):
    return await delete_role_by_id(db, role_id)