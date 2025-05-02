import os
from fastapi import HTTPException, Depends, Query
from typing import Annotated, List, Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_db
from app.models import Base
from starlette import status
from app.core.security import decode_token, oauth2_bearer
from app.core.enums.enums import RoleEnum
from starlette.requests import Request
from app.core.logger import logger

class PaginationParams:
    def __init__(self, page: Optional[int] = Query(None, ge=1), limit: Optional[int] = Query(None, ge=1)):
        self.page = page
        self.limit = limit

DBSession = Annotated[AsyncSession, Depends(get_db)]
Pagination = Annotated[PaginationParams, Depends()]

async def get_user_by_token(token: str = Depends(oauth2_bearer)):
    payload = await decode_token(token, os.getenv("SECRET_KEY"))
    username: str = payload.get("sub")
    user_id: str = payload.get("id")
    role: str = payload.get("role")

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    return {"username": username, "id": user_id, "role": role}

async def validate_roles(request: Request, roles: List[str]):
    auth_user_id = request.state.user.get("id")
    auth_user_role = request.state.user.get("role")

    if not auth_user_id or not auth_user_role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token')

    if auth_user_role not in roles:
        logger.error(f"User with id: {auth_user_id} and role: '{auth_user_role}' does not have permission to perform this action. "
                     f"Path: {request.url}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )
    return request.state.user

def allowed_roles(roles: List[str]):
    async def dependency(request: Request):
        return await validate_roles(request, roles)
    return dependency

async def check_resource_ownership(db: DBSession, resource_model: Type[Base], resource_id: int, request: Request):
    auth_user_id = request.state.user.get("id")

    result = await db.execute(
        select(resource_model)
        .filter(resource_model.id == resource_id)  # type: ignore
    )
    resource = result.scalars().first()

    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"{resource_model.__name__} not found")

    if resource.user_id != auth_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You do not have permission to perform this action')

    return resource

# Roles dependencies
SuperAdminSession = Depends(allowed_roles([RoleEnum.SUPER_ADMIN]))
BusinessSession = Depends(allowed_roles([RoleEnum.BUSINESS]))
ClientSession = Depends(allowed_roles([RoleEnum.CLIENT]))
EmployeeSession = Depends(allowed_roles([RoleEnum.EMPLOYEE]))
ClientAndEmployeeSession = Depends(allowed_roles([RoleEnum.CLIENT, RoleEnum.EMPLOYEE]))
BusinessAndEmployeesSession = Depends(allowed_roles([RoleEnum.BUSINESS, RoleEnum.EMPLOYEE]))

# Auth and db dependencies
UserSession = Depends(get_user_by_token)