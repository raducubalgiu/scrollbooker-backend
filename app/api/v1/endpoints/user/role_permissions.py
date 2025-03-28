from fastapi import APIRouter
from app.core.dependencies import DBSession
from app.schema.user.role_permissions import RolePermissionsResponse, RolePermissionsCreate
from app.service.user.role_permissions import attach_permission_to_role

router = APIRouter()

@router.post("/role-permissions", response_model=RolePermissionsResponse)
async def create_role_permissions(db: DBSession, role_permissions: RolePermissionsCreate):
    role = await attach_permission_to_role(db, role_permissions.role_id, role_permissions.permission_id)
    print("NEW ROLE!!!", role)