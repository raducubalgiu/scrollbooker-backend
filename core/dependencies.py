import os

import httpx
from fastapi import HTTPException, Depends, Query, status, Request
from typing import Annotated, List, Type, Optional, cast

from redis.asyncio import Redis
from schema.auth.auth import RequestAuthUser

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import get_db
from models import Base
from core.security import decode_token, oauth2_bearer
from core.logger import logger
from core.redis_client import init_redis
from core.http_client import get_http_client
from .enums.role_enum import RoleEnum

class PaginationParams:
    def __init__(
            self,
            page: Optional[int] = Query(None, ge=1),
            limit: Optional[int] = Query(None, ge=1)
    ):
        self.page = page
        self.limit = limit

DBSession: TypeAlias = Annotated[AsyncSession, Depends(get_db)]
HTTPClient: TypeAlias = Annotated[httpx.AsyncClient, Depends(get_http_client)]
RedisClient: TypeAlias = Annotated[Redis, Depends(init_redis)]
Pagination: TypeAlias = Annotated[PaginationParams, Depends()]

async def get_user_by_token(token: str = Depends(oauth2_bearer)) -> RequestAuthUser:
    payload = await decode_token(token, os.getenv("SECRET_KEY"))

    if payload and payload.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    return RequestAuthUser(
        id=payload.id,
        username=payload.username,
        email=payload.email,
        role=payload.role
    )

def get_authenticated_user_from_request(request: Request) -> RequestAuthUser:
    user = getattr(request.state, "user", None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token'
        )

    return cast(RequestAuthUser, user)


AuthenticatedUser = Annotated[RequestAuthUser, Depends(get_authenticated_user_from_request)]

async def validate_roles(auth_user: AuthenticatedUser, roles: List[str]):
    auth_user_id = auth_user.id
    auth_user_role = auth_user.role

    if not auth_user_id or not auth_user_role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token')

    if auth_user_role not in roles:
        logger.error(f"User with id: {auth_user_id} and role: '{auth_user_role}' does not have permission to perform this action")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to perform this action'
        )
    return auth_user

def allowed_roles(roles: List[str]):
    async def dependency(auth_user: AuthenticatedUser):
        return await validate_roles(auth_user, roles)
    return dependency

async def check_resource_ownership(
        db: DBSession,
        resource_model: Type[Base],
        resource_id: int,
        auth_user: AuthenticatedUser
):
    auth_user_id = auth_user.id

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
ManagerSession = Depends(allowed_roles([RoleEnum.MANAGER]))
ClientSession = Depends(allowed_roles([RoleEnum.CLIENT]))
EmployeeSession = Depends(allowed_roles([RoleEnum.EMPLOYEE]))

ClientAndEmployeeSession = Depends(allowed_roles([RoleEnum.CLIENT, RoleEnum.EMPLOYEE]))
ClientAndBusinessSession = Depends(allowed_roles([RoleEnum.CLIENT, RoleEnum.BUSINESS]))
BusinessAndEmployeesSession = Depends(allowed_roles([RoleEnum.BUSINESS, RoleEnum.EMPLOYEE]))
BusinessAndManagerSession = Depends(allowed_roles([RoleEnum.BUSINESS, RoleEnum.MANAGER]))

# Auth dependencies
UserSession = Depends(get_user_by_token)