from sqlalchemy import Boolean
from app.core.crud_helpers import db_delete, db_create, db_get_all
from app.models.user.role import Role
from app.schema.user.role import RoleCreate
from app.core.dependencies import DBSession

async def get_all_roles(db: DBSession):
    return await db_get_all(db, model=Role)

async def create_new_role(db: DBSession, new_role: RoleCreate):
    active= new_role.active if new_role.active == Boolean else True
    return await db_create(db, model=Role, create_data=new_role, extra_params={"active": active})

async def delete_role_by_id(db: DBSession, role_id: int):
    return await db_delete(db, model=Role, resource_id=role_id)