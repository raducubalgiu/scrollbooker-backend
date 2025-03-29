from typing import List
from sqlalchemy.orm import joinedload
from starlette.requests import Request
from fastapi import HTTPException, Query

from app.core.data_utils import local_to_utc_fulldate
from app.core.dependencies import DBSession
from starlette import status
from app.models import Business, Service, business_services, Product, Appointment, User, UserCounters, Schedule, Follow, \
    SubFilter, EmploymentRequest
from sqlalchemy import select, delete, and_, or_, func, not_, exists, text, insert
from pytz import timezone, utc #type: ignore
from geoalchemy2.shape import to_shape # type: ignore
from geoalchemy2 import Geography # type: ignore
from geoalchemy2.functions import ST_DistanceSphere # type: ignore
from timezonefinder import TimezoneFinder # type: ignore

from app.models.booking.product_sub_filters import product_sub_filters
from app.schema.booking.business import BusinessCreate, BusinessEmployeesResponse
from datetime import timedelta,datetime

async def get_business_employees_by_id(db: DBSession, business_id: int, page: int, limit: int):
   stmt = ((select(User, UserCounters, EmploymentRequest.created_at.label("hire_date"))
           .join(EmploymentRequest, and_(
                  EmploymentRequest.business_id == business_id,
                  EmploymentRequest.employee_id == User.id)
            )
            .join(UserCounters, UserCounters.user_id == User.id) # type: ignore
           .where(User.business_employee_id == business_id) #type: ignore
        ).order_by("hire_date"))

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
        distance_expr = func.ST_Distance(Business.location.cast(Geography), user_point.cast(Geography)) / 1000

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
            .join(User, or_( Business.owner_id == User.id, Business.id == User.business_employee_id))
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
                        Business.id == User.business_employee_id,
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

async def create_new_business(db: DBSession, business_data: BusinessCreate):
    longitude, latitude = business_data.location

    tf = TimezoneFinder()
    timezone = tf.timezone_at_land(lng=longitude, lat=latitude)

    stmt_owner_has_business = await db.execute(
        select(Business).
        filter(Business.owner_id == business_data.owner_id) # type: ignore
    )
    owner_has_business = stmt_owner_has_business.scalars().first()

    if owner_has_business:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You already have a business attached')

    stmt = text("""
        INSERT INTO businesses (description, address, location, timezone, owner_id) 
        VALUES (:description, :address, ST_SetSRID(ST_Point(:longitude, :latitude), 4326), :timezone, :owner_id)
        RETURNING id
    """)

    params = {
        "description": business_data.description,
        "address": business_data.address,
        "longitude": longitude,
        "latitude": latitude,
        "timezone": timezone,
        "owner_id": business_data.owner_id
    }
    result = await db.execute(stmt, params)
    business_id = result.scalar()
    await db.commit()
    return { "detail": "Business created", "id": business_id }

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

async def attach_service_to_business(db: DBSession, business_id: int, service_id: int, request: Request):
    authenticated_user_id = request.state.user.get("id")
    business = await db.get(Business, business_id)
    service = await db.get(Service, service_id)

    if business and service:
        if authenticated_user_id != business.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You do not have permission to perform this action')

        is_present = await db.execute(
            select(business_services).where(
                (business_services.c.business_id == business_id) & (business_services.c.service_id == service_id) # type: ignore
            )
        )

        if is_present.scalar():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='This service is already associated with this Business')

        await db.execute(insert(business_services).values(business_id=business_id, service_id=service_id))
        await db.commit()
        return {"detail": f"Service {service_id} successfully attached to Business {business_id}"}

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Business or service not found')


async def detach_service_from_business(db: DBSession, business_id: int, service_id: int, request: Request):
    authenticated_user_id = request.state.user.get("id")
    business = await db.get(Business, business_id)
    service = await db.get(Service, service_id)

    if business and service:
        if authenticated_user_id != business.owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You do not have permission to perform this action')

        is_present = await db.execute(
            select(business_services).where(
                (business_services.c.business_id == business_id) & (business_services.c.service_id == service_id) # type: ignore
            )
        )

        if not is_present.scalar():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='This service is not associated with this Business')

        await db.execute(delete(business_services).where(
            (business_services.c.business_id == business_id) & (business_services.c.service_id == service_id) # type: ignore
        ))
        await db.commit()

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Business or service not found')