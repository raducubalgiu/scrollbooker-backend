from typing import Optional

from geoalchemy2 import Geography
from sqlalchemy.orm import Query
from sqlalchemy import select, or_, func, asc
from core.dependencies import DBSession
from core.enums.role_enum import RoleEnum
from models import SearchKeyword, User, Service, BusinessType, UserCounters, Business, Role
from schema.search.search import SearchResponse, SearchServiceBusinessTypeResponse, SearchUserResponse

async def search_keyword(
        db: DBSession,
        query: str = Query,
        lat: Optional[float] = None,
        lng: Optional[float] = None
):
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
        SearchResponse(type="keyword", label=row.keyword)
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
        .where(or_(
            User.username.ilike(f"%{query}%"),
            User.fullname.ilike(f"%{query}%"),
            User.profession.ilike(f"%{query}%")
        ))
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