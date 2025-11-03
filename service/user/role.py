from core.crud_helpers import db_delete, db_create, db_get_all, db_update, PaginatedResponse
from models.user.role import Role
from schema.user.role import RoleCreate, RoleResponse, RoleUpdate
from core.dependencies import DBSession

async def get_all_roles(
        db: DBSession,
        page: int,
        limit: int
) -> PaginatedResponse[RoleResponse]:
    return await db_get_all(
        db=db,
        model=Role,
        schema=RoleResponse,
        page=page,
        limit=limit
    )

async def create_new_role(db: DBSession, role_create: RoleCreate):
    return await db_create(db, model=Role, create_data=role_create)

async def update_role_by_id(db: DBSession, role_id: int, role_update: RoleUpdate):
    return await db_update(db, model=Role, resource_id=role_id, update_data=role_update)

async def delete_role_by_id(db: DBSession, role_id: int):
    return await db_delete(db, model=Role, resource_id=role_id)