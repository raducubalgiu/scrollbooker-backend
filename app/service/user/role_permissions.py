from fastapi import HTTPException
from app.core.dependencies import DBSession
from app.models import Permission, Role

async def attach_permission_to_role(db: DBSession, role_id: int, permission_id: int):
    role = await db.get(Role, role_id)
    permission = await db.get(Permission, permission_id)

    if role is None or permission is None:
        raise HTTPException(status_code=404, detail='Role or permission not found')

    # Check if the permission is already assigned to avoid duplicates
    if permission in role.permissions:
        raise HTTPException(status_code=400, detail='Permission already asigned to this role')

    role.permissions.append(permission)

    await db.commit()