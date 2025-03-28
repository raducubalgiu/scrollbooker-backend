from fastapi import HTTPException

from app.core.crud_helpers import db_create, db_delete, db_get_one, db_get_all
from app.core.dependencies import DBSession
from sqlalchemy.future import select
from app.models import Permission
from app.schema.user.permission import PermissionCreate

async def get_all_permissions(db: DBSession):
    await db_get_all(db, model=Permission)

async def get_permission_by_id(db: DBSession, permission_id: int):
    await db_get_one(db, model=Permission, filters={Permission.id: permission_id})

async def create_new_permission(db: DBSession, new_permission: PermissionCreate):
    await db_create(db, model=Permission, create_data=new_permission)

async def delete_permission_by_id(db: DBSession, permission_id: int):
    await db_delete(db, model=Permission, resource_id=permission_id)

