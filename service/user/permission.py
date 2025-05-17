from typing import List, Dict, Any
from sqlalchemy import select,desc

from backend.core.crud_helpers import db_create, db_delete, db_insert_many_to_many, db_remove_many_to_many, db_update
from backend.core.dependencies import DBSession
from backend.models import Permission, Role
from backend.models.user.role_permissions import role_permissions
from backend.schema.user.permission import PermissionCreate, PermissionWithRolesResponse, RoleAssignment, PermissionUpdate

async def get_all_permissions(db: DBSession, page: int, limit: int):
    roles_result = await db.scalars(select(Role))
    roles = roles_result.all()

    permissions_result = await db.scalars(select(Permission).order_by(desc(Permission.created_at)).offset((page - 1) * limit).limit(limit))
    permissions = permissions_result.all()

    permissions_count_results = await db.scalars(select(Permission))
    permissions_count = len(permissions_count_results.all())

    assignment_result = await db.execute(select(
        role_permissions.c.role_id,
        role_permissions.c.permission_id
    ))
    assignments = assignment_result.all()
    assignment_set = {(r_id, p_id) for r_id, p_id in assignments}

    data: List[PermissionWithRolesResponse] = []

    for permission in permissions:
        role_assignments = [
            RoleAssignment(
                id= role.id,
                name=role.name,
                assigned=(role.id, permission.id) in assignment_set
            )
            for role in roles
        ]

        data.append(PermissionWithRolesResponse(
            id=permission.id,
            name=permission.name,
            code=permission.code,
            roles=role_assignments
        ))

    return {
        "count": permissions_count,
        "results": data
    }

async def create_new_permission(db: DBSession, permission_create: PermissionCreate):
    return await db_create(db, model=Permission, create_data=permission_create)

async def update_permission_by_id(db: DBSession, permission_id: int, permission_update: PermissionUpdate):
    return await db_update(db, model=Permission, resource_id=permission_id, update_data=permission_update)

async def delete_permission_by_id(db: DBSession, permission_id: int):
    return await db_delete(db, model=Permission, resource_id=permission_id)

async def attach_role_to_permission(db: DBSession, permission_id: int, role_id: int):
    return await db_insert_many_to_many(db,
                                        model_one=Role,
                                        resource_one_id=role_id,
                                        model_two=Permission,
                                        resource_two_id=permission_id,
                                        relation_table=role_permissions)

async def detach_role_from_permission(db: DBSession, permission_id: int, role_id: int):
    return await db_remove_many_to_many(db,
                                        model_one=Role,
                                        resource_one_id=role_id,
                                        model_two=Permission,
                                        resource_two_id=permission_id,
                                        relation_table=role_permissions)

