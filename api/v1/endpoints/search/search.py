from typing import Optional, Union

from fastapi import APIRouter
from fastapi.params import Query
from sqlalchemy import false
from starlette.requests import Request

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession
from schema.search.search import SearchResponse
from schema.user.user import UserBaseMinimum
from service.search.search import search_keyword, search_all_users

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/",
            summary='Search keywords, users, services or business types',
            response_model=list[SearchResponse])
async def search(
        db: DBSession,
        query: str = Query(min_length=1),
        lat: Optional[float] = None,
        lng: Optional[float] = None
):
    return await search_keyword(db, query, lat, lng)

@router.get("/users",
            summary='Search Users',
            response_model=Union[PaginatedResponse[UserBaseMinimum], list[UserBaseMinimum]])
async def search_users(
        db: DBSession,
        query: str,
        request: Request,
        page: Optional[int] = None,
        limit: Optional[int] = 10,
        role_client: Optional[bool] = False
):
    return await search_all_users(db, query, request, page, limit, role_client)