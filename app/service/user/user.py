from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from starlette import status
from starlette.requests import Request
from app.core.crud_helpers import db_get_all, db_get_all_paginate, db_get_one
from app.core.dependencies import DBSession
from app.core.enums.enums import RoleEnum
from app.models import Schedule, Review, User, Follow, Appointment, Product, Business, BusinessType, SubFilter, \
    Notification
from sqlalchemy import select, func, case, and_, or_
from app.schema.booking.product import ProductWithSubFiltersResponse
from app.schema.booking.business import BusinessResponse
from geoalchemy2.shape import to_shape # type: ignore

from app.schema.user.notification import NotificationResponse


async def search_users_clients(db: DBSession, q: str):
    query = select(User).filter(User.role_id == 2) #type: ignore

    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.fullname.ilike(search_term)
            )
        )

    users_stmt = await db.execute(query.order_by(User.username.asc()).limit(50))
    users = users_stmt.scalars().all()
    return users

async def get_user_business_by_id(db: DBSession, user_id: int):
    business_query = await db.execute(select(Business, User.id).where(
        and_(
            User.id == user_id,
            or_(
                Business.owner_id == user_id,
                Business.id == User.employee_business_id
            )
        )).options(joinedload(Business.services))
    )

    business = business_query.unique().scalar_one_or_none()

    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Business not found')

    point = to_shape(business.coordinates)
    latitude = point.y
    longitude = point.x

    return BusinessResponse(
        id=business.id,
        business_type_id=business.business_type_id,
        owner_id=business.owner_id,
        description=business.description,
        timezone=business.timezone,
        address=business.address,
        services=business.services,
        coordinates=(longitude, latitude)
    )

async def get_user_schedules_by_id(db: DBSession, user_id: int):
    await get_user_business_by_id(db, user_id)
    schedules = await db_get_all(db, model=Schedule, filters={Schedule.user_id: user_id}, order_by="day_week_index")

    return schedules

async def get_user_products_by_id(db: DBSession, user_id: int, page: int, limit: int):
    return await db_get_all_paginate(db,
                model=Product, filters={Product.user_id: user_id}, schema=ProductWithSubFiltersResponse , page=page, limit=limit,
                unique=True, joins=[joinedload(Product.sub_filters).joinedload(SubFilter.filter)])


async def get_user_dashboard_summary_by_id(db: DBSession, user_id: int, start_date: str, end_date:str):
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Start date and end date should use the format - %Y-%m-%d")

    days_diff = end_date_obj - start_date_obj
    previous_start_date = start_date_obj - days_diff
    previous_end_date = end_date_obj - days_diff

    def build_query(s_date, e_date, u_id):
        return (
            select(
                User.id.label("user_id"),
                func.coalesce(func.sum(Product.price), 0).label("total_sales"),
                func.coalesce(func.count(Appointment.id), 0).label("total_bookings"),
                func.coalesce(
                    func.sum(case((Appointment.channel == "closer_app", 1), else_=0)), 0 #type: ignore
                ).label("closer_bookings"),
                func.coalesce(
                    func.sum(case((Appointment.channel == "own_client", 1), else_=0)), 0 #type: ignore
                ).label("own_bookings"),
            )
            .outerjoin(Appointment, Appointment.user_id == User.id)  # type: ignore
            .outerjoin(Product, Product.id == Appointment.product_id)
            .where(
                and_(
                    Appointment.user_id == u_id,
                    Appointment.created_at >= s_date,
                    Appointment.created_at <= e_date
                )
            )
            .group_by(User.id)
        )

    current_result = await db.execute(build_query(start_date_obj, end_date_obj, user_id))
    previous_result = await db.execute(build_query(previous_start_date, previous_end_date, user_id))

    current_data = current_result.mappings().first()
    previous_data = previous_result.mappings().first()

    def calculate_trend(current, previous):
        if previous == 0:
            return "up" if current > 0 else "no_change", "100%" if current > 0 else "%0"
        percentage_change = ((current - previous) / previous) * 100 if previous else 0
        trend = "up" if percentage_change > 0 else "down"
        return trend, f"{percentage_change:.2f}%"

    response = []
    for key, title in [
        ('total_bookings', 'Total Bookings'),
        ('own_bookings', 'Own bookings'),
        ('closer_bookings', 'Closer Bookings'),
        ('total_sales', 'Total Sales'),
    ]:
        current_value = current_data[key] if current_data else 0
        previous_value = previous_data[key] if previous_data else 0
        trend, percentage = calculate_trend(current_value, previous_value)

        response.append({
            'title': title,
            'amount': current_value,
            'trend': trend,
            'percentage': percentage,
            "days_diff": days_diff.days
        })

    return response


async def get_user_reviews_by_user_id(db: DBSession, user_id: int, page: int, size: int):
    stmt = await db.execute(
        select(User)
        .filter(User.id == user_id) # type: ignore
        .options(joinedload(User.role))
    )
    user = stmt.scalars().first()
    role = user.role

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found!')

    field = 'customer_id' if role == 'client' else 'user_id'

    stmt = await db.execute(
        select(Review)
        .where(getattr(Review, field) == user_id) #type: ignore
        .options(
            joinedload(Review.service),
        )
        .offset((page - 1) * size)
        .limit(size)
    )

    reviews = stmt.scalars().unique().all()
    return reviews

async def get_user_followers_by_user_id(db: DBSession, user_id: int, page: int, limit: int, request: Request):
   auth_user_id = request.state.user.get("id")

   subquery = (
       select(Follow)
       .where(Follow.follower_id == auth_user_id, Follow.followee_id == User.id) #type: ignore
       .correlate(User)
       .exists()
   )

   query = await db.execute((
       select(User.id, User.username, User.fullname, User.avatar, subquery.label("is_follow"))
       .join(Follow, Follow.follower_id == User.id) # type: ignore
       .where(Follow.followee_id == user_id)
       .offset((page - 1) * limit)
       .limit(limit)
   ))
   followers = query.mappings().all()
   return followers

async def get_user_followings_by_user_id(db: DBSession, user_id: int, page: int, limit: int, request: Request):
   auth_user_id = request.state.user.get("id")

   subquery = (
       select(Follow)
       .where(Follow.follower_id == auth_user_id, Follow.followee_id == User.id) # type: ignore
       .correlate(User)
       .exists()
   )

   query = await db.execute(
       select(User.id, User.username, User.avatar, subquery.label("is_follow"))
       .join(Follow, Follow.followee_id == User.id) #type: ignore
       .where(Follow.follower_id == user_id)
       .offset((page - 1) * limit)
       .limit(limit)
   )

   followings = query.mappings().all()
   return followings

async def get_user_notifications_by_id(db: DBSession, page: int, limit: int):
    return await db_get_all_paginate(db,
                                     model=Notification,
                                     schema=NotificationResponse,
                                     filters={Notification.is_deleted: False},
                                     joins=[joinedload(Notification.sender)],
                                     page=page,
                                     limit=limit)


# If Business - return Business Types, if employee - return Professions
async def get_available_professions_by_user_id(db: DBSession, user_id: int):
    user = await db_get_one(db,
                            model=User,
                            filters={User.id: user_id},
                            joins=[joinedload(User.role),
                                   joinedload(User.owner_business),
                                   joinedload(User.employee_business)]
                            )

    if user.role.name == RoleEnum.BUSINESS:
        business = await db_get_one(db, model=Business, filters={Business.owner_id: user.id},
                        joins=[joinedload(Business.business_type).load_only(BusinessType.business_domain_id)])

        business_types = await db_get_all(db, model=BusinessType,
                            filters={BusinessType.business_domain_id: business.business_type.business_domain_id})
        return business_types

    if user.role.name == RoleEnum.EMPLOYEE:
        stmt = await db.execute(
            select(BusinessType)
            .options(joinedload(BusinessType.professions))
            .where(BusinessType.id == user.employee_business.business_type_id) #type: ignore
        )
        business_type = stmt.scalars().first()
        professions = business_type.professions
        return professions