from sqlalchemy.orm import Query
from sqlalchemy import select, or_
from core.dependencies import DBSession
from models import SearchKeyword, User, Service, BusinessType, UserCounters
from schema.search.search import SearchResponse, SearchServiceBusinessTypeResponse
from schema.user.user import UserBaseMinimum

async def search_keyword(db: DBSession, query: str = Query):
    max_per_type = 10

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
        select(User.id, User.fullname, User.username, User.profession, User.avatar, UserCounters.ratings_average)
        .join(UserCounters, UserCounters.user_id == User.id)
        .where(or_(
            User.username.ilike(f"%{query}%"),
            User.fullname.ilike(f"%{query}%"),
            User.profession.ilike(f"%{query}%")
        ))
        .limit(max_per_type)
    )
    users_result = await db.execute(stmt_users)

    users = [
        SearchResponse(
            type="user",
            label=user.fullname,
            user=UserBaseMinimum(
                id=user.id,
                fullname= user.fullname,
                username= user.username,
                profession= user.profession,
                avatar= user.avatar,
                ratings_average=user.ratings_average
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