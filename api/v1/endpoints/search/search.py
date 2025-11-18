from typing import Optional, Union, List
from fastapi import APIRouter, Query, Request, status

from core.crud_helpers import PaginatedResponse
from core.dependencies import DBSession, AuthenticatedUser, Pagination
from schema.search.search import SearchResponse, SearchCreate, UserSearchHistoryResponse, SearchUserResponse
from service.search.search import search_keyword, search_all_users, create_user_search, get_user_search_history, \
    delete_user_search

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/",
            summary='Search keywords, users, services or business types',
            response_model=List[SearchResponse])
async def search(
        db: DBSession,
        query: str = Query(min_length=1),
        lat: Optional[float] = None,
        lng: Optional[float] = None
) -> List[SearchResponse]:
    return await search_keyword(db, query, lat, lng)

@router.get("/users",
            summary='Search Users',
            response_model=Union[PaginatedResponse[SearchUserResponse], List[SearchUserResponse]])
async def search_users(
        db: DBSession,
        query: str,
        auth_user: AuthenticatedUser,
        pagination: Pagination,
        role_client: Optional[bool] = False
) -> Union[PaginatedResponse[SearchUserResponse], List[SearchUserResponse]]:
    return await search_all_users(db, query, auth_user, pagination, role_client)

@router.get("/user-history",
            summary='List User Search History')
async def get_user_search(
        db: DBSession,
        auth_user: AuthenticatedUser,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        timezone: Optional[str] = None
):
    return await get_user_search_history(db, auth_user, lat, lng, timezone)

@router.post("/user-history",
            summary="Create Search keyword",
            response_model=UserSearchHistoryResponse)
async def create_search(
        db: DBSession,
        search_create: SearchCreate,
        auth_user: AuthenticatedUser
) -> UserSearchHistoryResponse:
    return await create_user_search(db, search_create, auth_user)

@router.delete("/user-history/{search_id}",
               summary="Delete User Search",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_search(db: DBSession, search_id: int):
    return await delete_user_search(db, search_id)