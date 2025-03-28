from fastapi import APIRouter
from starlette import status
from app.core.dependencies import DBSession, SuperAdminSession
from app.schema.user.permission import PermissionResponse, PermissionCreate
from app.service.user.permission import get_all_permissions, create_new_permission, delete_permission_by_id, get_permission_by_id

router = APIRouter(prefix="/permissions", tags=["Permissions"])

@router.get("/", response_model=list[PermissionResponse])
async def get_permissions(db: DBSession):
    return await get_all_permissions(db)

@router.post("/", response_model=PermissionResponse, dependencies=[SuperAdminSession])
async def create_permission(db: DBSession, new_permission: PermissionCreate):
    return await create_new_permission(db, new_permission)

@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(db: DBSession, permission_id: int):
    return await get_permission_by_id(db, permission_id)

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[SuperAdminSession])
async def delete_permission(db: DBSession, permission_id: int):
    return await delete_permission_by_id(db, permission_id)