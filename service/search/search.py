from typing import Optional, List, Union
from geoalchemy2 import Geography
from sqlalchemy.orm import Query
from sqlalchemy import select, or_, func, and_, desc
from starlette.requests import Request

from core.crud_helpers import db_delete, PaginatedResponse
from core.dependencies import DBSession, AuthenticatedUser, Pagination
from core.enums.role_enum import RoleEnum
from models import SearchKeyword, User, Service, BusinessType, UserCounters, Business, Role, Follow, UserSearchHistory
from schema.search.search import SearchResponse, SearchServiceBusinessTypeResponse, SearchUserResponse, SearchCreate,  UserSearchHistoryResponse
from service.booking.business import get_user_recommended_businesses

async def search_keyword(
        db: DBSession,
        query: str = Query,
        lat: Optional[float] = None,
        lng: Optional[float] = None
) -> List[SearchResponse]:
    max_per_type = 10

    user_point = func.ST_SetSRID(func.ST_Point(lng, lat), 4326)
    distance_expr = func.ST_Distance(Business.coordinates.cast(Geography), user_point.cast(Geography)) / 1000

    stmt_keywords = (
        select(SearchKeyword)
        .where(SearchKeyword.keyword.ilike(f"%{query}%"))
        .order_by(SearchKeyword.count.desc())
        .limit(max_per_type)
    )

    keywords_result = await db.execute(stmt_keywords)
    keywords = [
        SearchResponse(type="keyword", label=row.keyword, user=None, service=None, business_type=None)
        for row in keywords_result.scalars()
    ]

    stmt_users = (
        select(
            User.id,
            User.fullname,
            User.username,
            User.profession,
            User.avatar,
            Role.name.label("role_name"),
            UserCounters.ratings_average,
            distance_expr.label("distance")
        )
        .join(UserCounters, UserCounters.user_id == User.id)
        .join(Role, Role.id == User.role_id)
        .outerjoin(Business, or_(
            Business.id == User.employee_business_id,
            Business.owner_id == User.id
        ))
        .where(
            and_(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.fullname.ilike(f"%{query}%"),
                    User.profession.ilike(f"%{query}%"),
                ),
                User.is_validated == True,
                User.active == True
            )
        )
        .order_by("distance")
        .limit(max_per_type)
    )
    users_result = await db.execute(stmt_users)

    users = [
        SearchResponse(
            type="user",
            label=user.fullname,
            user=SearchUserResponse(
                id=user.id,
                fullname= user.fullname,
                username= user.username,
                profession= user.profession,
                avatar= user.avatar,
                ratings_average=user.ratings_average,
                distance=round(user.distance, 1) if user.role_name is RoleEnum.BUSINESS and user.distance is not None else None,
                is_business_or_employee=user.role_name in [RoleEnum.EMPLOYEE, RoleEnum.BUSINESS]
            ),
            service=None,
            business_type=None
        ) for user in users_result.mappings().all()
    ]

    stmt_services = (
        select(Service.id, Service.name)
        .where(Service.name.ilike(f"%{query}%"))
        .limit(max_per_type)
    )
    services_result = await db.execute(stmt_services)
    services = [
        SearchResponse(
            type="service",
            label=service.name,
            user=None,
            service=SearchServiceBusinessTypeResponse(
                id=service.id,
                name=service.name
            ),
            business_type=None
        )
        for service in services_result.mappings().all()
    ]

    stmt_bt = (
        select(BusinessType.id, BusinessType.name)
        .where(BusinessType.name.ilike(f"%{query}%"))
        .limit(max_per_type)
    )
    bt_result = await db.execute(stmt_bt)
    business_types = [
        SearchResponse(
            type="business_type",
            label=business_type.name,
            user=None,
            service=None,
            business_type=SearchServiceBusinessTypeResponse(
                id=business_type.id,
                name=business_type.name
            )
        )
        for business_type in bt_result.mappings().all()
    ]

    results = []
    all_lists = [keywords, users, services, business_types]
    max_len = max(map(len, all_lists))
    for i in range(max_len):
        for lst in all_lists:
            if i < len(lst):
                results.append(lst[i])
            if len(results) >= 20:
                return results
    return results

async def search_all_users(
        db: DBSession,
        query: str,
        auth_user: AuthenticatedUser,
        pagination: Pagination,
        role_client: Optional[bool] = False
) -> Union[PaginatedResponse[SearchUserResponse], List[SearchUserResponse]]:
    auth_user_id = auth_user.id
    search_term = f"%{query}%"

    is_follow = (
        select(Follow)
        .where(
            and_(
                Follow.follower_id == auth_user_id,
                Follow.followee_id == User.id
            )
        )
        .correlate(User)
        .exists()
    )

    filters = [
        User.is_validated == True,
        User.active == True,
        or_(
            User.username.ilike(search_term),
            User.fullname.ilike(search_term)
        )
    ]

    if role_client:
        filters.append(Role.name == RoleEnum.CLIENT)

    stmt = (
        select(
            User.id, User.username, User.fullname, User.profession, User.avatar,
            is_follow.label("is_follow"),
            UserCounters.ratings_average.label("ratings_average")
        )
        .join(UserCounters, UserCounters.user_id == User.id)
        .join(Role, Role.id == User.role_id)
        .where(*filters)
    )

    if pagination.page is not None:
        count_smt = select(func.count()).select_from(
            select(User.id)
            .join(Role, Role.id == User.role_id)
            .where(*filters)
            .subquery()
        )

        count_result = await db.execute(count_smt)
        count = count_result.scalar_one()

        stmt = stmt.offset((pagination.page - 1) * pagination.limit)
        stmt = stmt.order_by(User.username.asc()).limit(pagination.limit)

        users_stmt = await db.execute(stmt)
        users = users_stmt.mappings().all()

        return PaginatedResponse(
            count=count,
            results=users
        )

    stmt = stmt.where(*filters).order_by(User.username.asc()).limit(pagination.limit)

    users_stmt = await db.execute(stmt)
    users = users_stmt.mappings().all()

    return users

async def get_user_search_history(
        db: DBSession,
        auth_user: AuthenticatedUser,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        timezone: Optional[str] = None
):
    auth_user_id = auth_user.id

    search_result = await db.execute(
        select(UserSearchHistory)
        .where(UserSearchHistory.user_id == auth_user_id)
        .order_by(desc(UserSearchHistory.created_at))
        .limit(20)
    )
    search = search_result.scalars().all()

    recommended_businesses = await get_user_recommended_businesses(db, lat, lng, timezone)

    return {
        "recommended_businesses": recommended_businesses,
        "recently_search": search
    }

async def create_user_search(
        db: DBSession,
        search_create: SearchCreate,
        auth_user: AuthenticatedUser
) -> UserSearchHistoryResponse:
    auth_user_id = auth_user.id

    result = await db.execute(
        select(SearchKeyword)
        .where(SearchKeyword.keyword == search_create.keyword)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.count += 1
    else:
        new_keyword = SearchKeyword(keyword=search_create.keyword)
        db.add(new_keyword)

    user_search_result = await db.execute(
        select(UserSearchHistory)
        .where(and_(
            UserSearchHistory.keyword == search_create.keyword,
            UserSearchHistory.user_id == auth_user_id
        ))
    )
    existing_user_search = user_search_result.scalar_one_or_none()

    if existing_user_search:
        existing_user_search.count += 1
        await db.commit()
        return UserSearchHistoryResponse(
            id=existing_user_search.id,
            keyword=existing_user_search.keyword,
            created_at=existing_user_search.created_at
        )

    new_user_search = UserSearchHistory(
        user_id=auth_user_id,
        keyword=search_create.keyword
    )
    db.add(new_user_search)
    await db.flush()

    await db.commit()

    return UserSearchHistoryResponse(
        id=new_user_search.id,
        keyword=new_user_search.keyword,
        created_at=new_user_search.created_at
    )

async def delete_user_search(db: DBSession, search_id: int):
    return await db_delete(db, model=UserSearchHistory, resource_id=search_id)

