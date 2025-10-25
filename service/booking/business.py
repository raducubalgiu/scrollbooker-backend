import os

from typing import List, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.orm import joinedload
from starlette.requests import Request
from fastapi import HTTPException, Query

from core.dependencies import RedisClient
from core.enums.day_of_week_enum import DayOfWeekEnum
from core.enums.registration_step_enum import RegistrationStepEnum
from core.logger import logger
from core.data_utils import local_to_utc_fulldate
from core.dependencies import DBSession, HTTPClient
from starlette import status
from models import Business, Service, Product, Appointment, User, UserCounters, Schedule, Follow, \
    SubFilter, EmploymentRequest, BusinessType
from sqlalchemy import select, and_, or_, func, not_, exists, text, literal_column
from geoalchemy2.shape import to_shape
from geoalchemy2 import Geography
from timezonefinder import TimezoneFinder

from models.booking.product_sub_filters import product_sub_filters
from schema.booking.business import BusinessCreate, BusinessResponse, BusinessHasEmployeesUpdate, \
    BusinessCreateResponse, BusinessCoordinates, RecommendedBusinessesResponse, RecommendedBusinessUser, \
    BusinessLocationResponse
from datetime import timedelta,datetime

from schema.integration.google import StaticMapQuery
from schema.user.user import UserAuthStateResponse
from service.integration.google import get_place_details, fetch_static_map

STATIC_MAP_ROUTE = os.getenv("STATIC_MAP_ROUTE")

async def get_business_by_id(db: DBSession, business_id: int) -> BusinessResponse:
    business_query = await db.execute(
        select(Business)
        .where(and_(Business.id == business_id))
        .options(joinedload(Business.services))
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
        coordinates=BusinessCoordinates(lat=latitude, lng=longitude),
        has_employees=business.has_employees
    )

async def get_business_location(
    db: DBSession,
    http_client: HTTPClient,
    redis_client: RedisClient,
    business_id: int,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
) -> BusinessLocationResponse:
    user_point = func.ST_SetSRID(func.ST_Point(user_lat, user_lng), 4326)
    distance_expr = func.ST_Distance(Business.coordinates.cast(Geography), user_point.cast(Geography)) / 1000

    business_query = await db.execute(
        select(Business.coordinates, Business.address, distance_expr.label("distance"))
        .where(and_(Business.id == business_id))
    )
    business = business_query.mappings().first()

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    point = to_shape(business.coordinates)
    business_lat = point.y
    business_lng = point.x

    map_url = (
        f"{STATIC_MAP_ROUTE}"
        f"?center_lat={business_lat}&center_lng={business_lng}"
        f"&zoom=15&width=640&height=360&scale=2"
        f"&language=ro&maptype=roadmap"
        f"&markers=color:red|{business_lat},{business_lng}"
        f"&style=feature:poi|visibility:off"
    )

    try:
        await fetch_static_map(
            http_client=http_client,
            redis_client=redis_client,
            query=StaticMapQuery(center_lat=business_lat, center_lng=business_lng)
        )
    except Exception as e:
        logger.error(f"The map could not be loaded. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Map could not be initialized"
        )

    return BusinessLocationResponse(
        distance = round(business.distance, 1) if business.distance else None,
        address=business.address,
        map_url=map_url
    )

async def get_business_by_user_id(db: DBSession, user_id: int) -> BusinessResponse:
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
        coordinates=BusinessCoordinates(lat=latitude, lng=longitude),
        has_employees=business.has_employees
    )

async def get_business_employees_by_id(db: DBSession, business_id: int, page: int, limit: int):
   stmt = (
       select(User, UserCounters, EmploymentRequest.created_at.label("hire_date"))
       .join(EmploymentRequest, and_(
              EmploymentRequest.business_id == business_id,
              EmploymentRequest.employee_id == User.id)
        )
        .join(UserCounters, UserCounters.user_id == User.id)
        .where(User.employee_business_id == business_id)
        ).order_by("hire_date")

   count_employees = await db.execute(stmt)
   count = len(count_employees.all())

   stmt_employees = await db.execute(stmt.offset((page - 1) * limit).limit(limit))
   employees = stmt_employees.all()

   return {
       "count": count,
       "results": [
           {
               "id": employee.id,
               "username": employee.username,
               "job": employee.profession,
               "followers_count": counters.followers_count,
               "ratings_count": counters.ratings_count,
               "ratings_average": counters.ratings_average,
               "hire_date": datetime.strftime(hire_date, '%Y-%d-%m')
           } for employee, counters, hire_date in employees
       ]
   }

async def get_user_recommended_businesses(
    db: DBSession,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    timezone: Optional[str] = None,
    limit: Optional[int] = 10
):
    if not timezone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Timezone was not provided'
        )

    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        raise ValueError(f"Invalid timezone: {timezone}")


    local_now = datetime.now(tz)
    current_time = local_now.time()
    day_str = local_now.strftime("%A")

    is_open_subquery = (
        select(literal_column("1"))
        .select_from(Schedule)
        .where(
            and_(
                Schedule.user_id == User.id,
                Schedule.day_of_week == day_str,
                Schedule.start_time <= current_time,
                Schedule.end_time >= current_time
            )
        )
        .limit(1)
        .correlate(User)
    )

    is_open = exists(is_open_subquery)

    user_point = func.ST_SetSRID(func.ST_Point(lng, lat), 4326)
    distance = func.ST_Distance(Business.coordinates.cast(Geography), user_point.cast(Geography)) / 1000

    query = (
        select(Business, User.id, User.fullname, User.username, User.profession, User.profession,
               UserCounters.ratings_average, distance, is_open)
        .join(User, User.id == Business.owner_id)
        .outerjoin(UserCounters, User.id == UserCounters.user_id)
        .order_by(distance, UserCounters.ratings_average)
        .limit(limit)
    )

    result = await db.execute(query)

    businesses = [
        RecommendedBusinessesResponse(
            user=RecommendedBusinessUser(
                id=u_id,
                fullname=u_fullname,
                username=u_username,
                avatar=u_avatar,
                profession=u_profession,
                ratings_average=u_ratings_average
            ),
            distance=round(distance, 2) if distance is not None else None,
            is_open=is_open
        ) for business, u_id, u_fullname, u_username, u_profession, u_avatar, u_ratings_average, distance, is_open in
        result.all()
    ]

    return businesses


async def get_businesses_by_distance(
        db: DBSession,
        lon: float,
        lat: float,
        start_date: str,
        end_date: str,
        start_time: str,
        end_time: str,
        service_id: int,
        instant_booking: bool,
        request: Request,
        page: int,
        limit: int,
        sub_filters: List[int] = Query([])
):
    auth_user_id = request.state.user.get("id")

    full_start = await local_to_utc_fulldate('Europe/Bucharest', start_date, start_time)
    full_end = await local_to_utc_fulldate('Europe/Bucharest', end_date, end_time)
    available_businesses = []

    while full_start <= full_end:
        daily_start = full_start
        daily_end = datetime.combine(full_start.date(), full_end.timetz())

        user_point = func.ST_SetSRID(func.ST_Point(lon, lat), 4326)
        distance_expr = func.ST_Distance(Business.coordinates.cast(Geography), user_point.cast(Geography)) / 1000

        availability_condition = or_(
            not_(
                exists().where(
                    and_(
                        Appointment.user_id == User.id,
                        Appointment.start_date < daily_end,
                        Appointment.end_date > daily_start,
                    )
                )
            ),
            exists().where(
                and_(
                    Appointment.user_id == User.id,
                    Appointment.start_date < daily_end,
                    Appointment.end_date > daily_start,
                    or_(
                        Appointment.start_date > daily_start,
                        Appointment.end_date < daily_end,
                    )
                )
            )
        )

        filter_business_or_employee = (
            and_(
                Schedule.day_of_week == daily_start.strftime("%A"),
                Schedule.start_time <= daily_start.timetz(),
                Schedule.end_time >= daily_end.timetz(),
                Service.id == service_id,
                SubFilter.id.in_(sub_filters),
                *( [User.instant_booking == True] if instant_booking else []),
                availability_condition
            )
        )

        is_follow_subquery = (
            select(Follow)
            .where(Follow.follower_id == auth_user_id, Follow.followee_id == Business.owner_id)  # type: ignore
            .correlate(User)
            .exists()
        )

        business_query = (
            select(Business,
                   func.sum(UserCounters.ratings_count).label("sum_ratings_count"),
                   func.avg(UserCounters.ratings_average).label("avg_ratings_average"),
                   func.min(Product.price).label("min_price"),
                   distance_expr.label("distance"),
                   is_follow_subquery.label("is_follow")
            )
            .join(User, or_( Business.owner_id == User.id, Business.id == User.employee_business_id))
            .join(Schedule, Schedule.user_id == User.id) #type: ignore
            .join(UserCounters, UserCounters.user_id == User.id)
            .join(Product, Product.user_id == User.id)
            .join(Service, Service.id == Product.service_id)
            .join(product_sub_filters, Product.id == product_sub_filters.c.product_id)
            .join(SubFilter, product_sub_filters.c.sub_filter_id == SubFilter.id)
            .where(
                or_(
                    and_(
                        Business.has_employees == True,
                        Business.id == User.employee_business_id,
                        filter_business_or_employee
                    ),
                    and_(
                        Business.has_employees == False,
                        Business.owner_id == User.id,
                        filter_business_or_employee
                    )
                )
            )
            .options(
                joinedload(Business.business_owner).load_only(User.id, User.username).joinedload(User.counters).load_only(UserCounters.followers_count),
                joinedload(Business.employees).load_only(User.id, User.username)
            )
            .group_by(Business.id, User.id, UserCounters.ratings_count, UserCounters.ratings_average)
            .order_by("distance", "sum_ratings_count", "avg_ratings_average", "min_price")
            .limit(limit)
            .offset((page - 1) * limit)
        )

        results = await db.execute(business_query)
        businesses = results.unique().all()

        for business, sum_ratings_count, avg_ratings_average, min_price, distance, is_follow in businesses:
                new_business = {
                      "id": business.id,
                      "business_owner": {
                          "id": business.business_owner.id,
                          "username": business.business_owner.username,
                          "followers_count": business.business_owner.counters.followers_count,
                          "is_follow": is_follow,
                      },
                      "address": business.address,
                      #"employees": business.employees,
                      "min_price": round(min_price, 2),
                      "sum_ratings_count": sum_ratings_count,
                      "avg_ratings_average": round(avg_ratings_average, 1),
                        "distance": f"{round(distance, 1)} km",
                }

                if new_business not in available_businesses:
                    available_businesses.append(new_business)

        full_start += timedelta(days=1)

    return {
        "results": len(available_businesses),
        "available_businesses": available_businesses
    }

async def create_new_business(
        db: DBSession,
        client: HTTPClient,
        business_data: BusinessCreate,
        request: Request
):
    auth_user_id = request.state.user.get("id")

    try:
        place = await get_place_details(client, business_data.place_id)
        owner = await db.get(User, auth_user_id)
        business_type = await db.get(BusinessType, business_data.business_type_id)

        tf = TimezoneFinder()
        business_timezone = tf.timezone_at_land(lng=place.lng, lat=place.lat)

        stmt_owner_has_business = await db.execute(
            select(Business).
            filter(and_(Business.owner_id == auth_user_id))
        )
        owner_has_business = stmt_owner_has_business.scalars().first()

        if owner_has_business:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You already have a business attached')

        stmt = text("""
            INSERT INTO businesses (description, address, coordinates, timezone, owner_id, business_type_id, has_employees)
            VALUES (:description, :address, ST_SetSRID(ST_Point(:longitude, :latitude), 4326), :timezone, :owner_id, :business_type_id, :has_employees)
            RETURNING id
        """)

        params = {
            "description": business_data.description,
            "address": place.address,
            "longitude": place.lng,
            "latitude": place.lat,
            "timezone": business_timezone,
            "owner_id": auth_user_id,
            "business_type_id": business_data.business_type_id,
            "has_employees": business_type.has_employees
        }

        if owner.registration_step is RegistrationStepEnum.COLLECT_BUSINESS:
            owner.registration_step = RegistrationStepEnum.COLLECT_BUSINESS_SERVICES

        owner.fullname = business_data.owner_fullname
        owner.profession = business_type.name

        db.add(owner)

        business_result = await db.execute(stmt, params)
        business_id = business_result.scalar_one()

        days_of_week = [
            (DayOfWeekEnum.MONDAY, 0),
            (DayOfWeekEnum.TUESDAY, 1),
            (DayOfWeekEnum.WEDNESDAY, 2),
            (DayOfWeekEnum.THURSDAY, 3),
            (DayOfWeekEnum.FRIDAY, 4),
            (DayOfWeekEnum.SATURDAY, 5),
            (DayOfWeekEnum.SUNDAY, 6)
        ]

        for day_of_week, index in days_of_week:
            schedule = Schedule(
                user_id=auth_user_id,
                business_id=business_id,
                day_of_week=day_of_week,
                start_time=None,
                end_time=None,
                day_week_index=index
            )
            db.add(schedule)

        await db.commit()
        await db.refresh(owner)

        return BusinessCreateResponse(
            authState=UserAuthStateResponse(
                is_validated=owner.is_validated,
                registration_step=owner.registration_step
            ),
            business_id=business_id
        )
    except Exception as e:
        await db.rollback()

        logger.error(f"Business could not be created. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Business could not be created')

async def update_business_has_employees(db: DBSession, business_update: BusinessHasEmployeesUpdate, request: Request):
    auth_user_id = request.state.user.get("id")

    try:
        business_stmt = await db.execute(
            select(Business)
            .where(and_(Business.owner_id == auth_user_id))
        )
        business = business_stmt.scalar_one_or_none()

        if not business:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='This Business was not found')
        if auth_user_id != business.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You do not have permission to perform this action')

        business.has_employees = business_update.has_employees
        db.add(business)
        await db.commit()
        await db.refresh(business)

        return await get_business_by_id(db, business_id=business.id)

    except Exception as e:
        logger.error(f"Business could not be updated. ERROR: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

async def delete_business_by_id(db: DBSession, business_id: int, request: Request):
    auth_user_id = request.state.user.get("id")
    business = await db.get(Business, business_id)

    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='This Business was not found')
    if auth_user_id != business.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You do not have permission to perform this action')

    await db.delete(business)
    await db.commit()