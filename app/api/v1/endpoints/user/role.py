from fastapi import APIRouter
from starlette import status
from app.core.dependencies import DBSession
from app.schema.user.role import RoleResponse, RoleCreate
from app.service.user.role import get_all_roles, create_new_role, delete_role_by_id

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("/", response_model=list[RoleResponse])
async def get_roles(db: DBSession):
    return await get_all_roles(db)

@router.post("/", response_model=RoleResponse)
async def create_role(db: DBSession, new_role: RoleCreate):
    return await create_new_role(db, new_role)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(db: DBSession, role_id: int):
    return await delete_role_by_id(db, role_id)