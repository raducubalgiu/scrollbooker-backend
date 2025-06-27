from fastapi import APIRouter
from starlette import status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, SuperAdminSession
from schema.user.permission import PermissionResponse, PermissionCreate, PermissionWithRolesResponse, \
    PermissionUpdate
from service.user.permission import get_all_permissions, create_new_permission, delete_permission_by_id, \
    attach_role_to_permission, detach_role_from_permission, update_permission_by_id

router = APIRouter(prefix="/permissions", tags=["Permissions"])

@router.get(
    "/",
    summary='List All Permissions',
    response_model=PaginatedResponse[PermissionWithRolesResponse])
async def get_permissions(db: DBSession, page: int, limit: int):
    return await get_all_permissions(db, page, limit)

@router.post(
    "/",
    summary='Create New Permission',
    response_model=PermissionResponse,
    dependencies=[SuperAdminSession])
async def create_permission(db: DBSession, permission_create: PermissionCreate):
    return await create_new_permission(db, permission_create)

@router.put(
    "/{permission_id}",
    summary='Update Permission',
    response_model=PermissionResponse,
    dependencies=[SuperAdminSession])
async def update_permission(db: DBSession, permission_id: int, permission_update: PermissionUpdate):
    return await update_permission_by_id(db, permission_id, permission_update)

@router.delete(
    "/{permission_id}",
    summary='Delete Permission',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def delete_permission(db: DBSession, permission_id: int):
    return await delete_permission_by_id(db, permission_id)

@router.post(
    "/{permission_id}/roles/{role_id}",
    summary='Create Role - Permission Relation',
    status_code=status.HTTP_201_CREATED,
    dependencies=[SuperAdminSession])
async def attach_role_permission(db: DBSession, permission_id: int, role_id: int):
    return await attach_role_to_permission(db, permission_id, role_id)

@router.delete(
    "/{permission_id}/roles/{role_id}",
    summary='Remove Role - Permission Relation',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SuperAdminSession])
async def detach_role_permission(db: DBSession, permission_id: int, role_id: int):
    return await detach_role_from_permission(db, permission_id, role_id)