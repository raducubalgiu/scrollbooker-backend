import random
from datetime import datetime, timezone, timedelta, date
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from fastapi.params import Depends
from geoalchemy2 import Geography
from sqlalchemy.orm import joinedload
from starlette import status
from starlette.requests import Request

from core.crud_helpers import db_get_all, db_get_one, db_update, PaginatedResponse
from core.dependencies import DBSession, AuthenticatedUser, Pagination
from core.enums.appointment_status_enum import AppointmentStatusEnum
from core.enums.role_enum import RoleEnum
from models import User, Follow, Appointment, Product, Business, Role, BusinessType, Schedule, UserCounters
from sqlalchemy import select, func, case, and_, or_, distinct, exists, literal_column
from schema.user.user import UsernameUpdate, FullNameUpdate, BioUpdate, GenderUpdate, UserProfileResponse, \
    OpeningHours, SearchUsername, SearchUsernameResponse, BirthDateUpdate, UserAuthStateResponse, \
    UserUpdateResponse, WebsiteUpdate, PublicEmailUpdate, UserProfileBusinessOwner, UserBaseMinimum


async def search_available_username(db: DBSession, query: SearchUsername = Depends()):
    result = await db.execute(select(User.id).where(and_(User.username == query.username)))
    user = result.scalar_one_or_none()

    if user is None:
        return SearchUsernameResponse(
            available=True,
            suggestions=[]
        )

    suggestions = await generate_username_suggestions(db, query.username)

    return SearchUsernameResponse(
        available=False,
        suggestions=suggestions
    )

async def generate_username_suggestions(db: DBSession, base: str, max_suggestions: int = 5):
    suggestions = []
    tried = set()

    while len(suggestions) < max_suggestions:
        suffix = random.choice([
            str(random.randint(1, 9999)),
            f"_{random.randint(10, 99)}",
            f"_{random.randint(100, 999)}",
            "_user"
        ])
        candidate = f"{base}{suffix}"
        if candidate in tried:
            continue
        tried.add(candidate)

        result = await db.execute(select(User.id).where(and_(User.username == candidate)))
        if result.scalar_one_or_none() is None:
            suggestions.append(candidate)
    return suggestions

async def get_user_profile_by_id(
        db: DBSession,
        user_id: int,
        auth_user: UserProfileResponse
) -> UserProfileResponse:
    auth_user_id = auth_user.id

    lat = 44.450653
    lng = 25.992614

    user_point = func.ST_SetSRID(func.ST_Point(lng, lat), 4326)
    distance_expr = (
            func.ST_Distance(Business.coordinates.cast(Geography), user_point.cast(Geography)) / 1000
    ).label("distance_km") if lat and lng else literal_column("NULL").label("distance_km")

    user_stmt = await db.execute(
        select(
            User.id,
            User.username,
            User.fullname,
            User.avatar,
            User.gender,
            User.bio,
            User.website,
            User.public_email,
            User.instagram,
            User.youtube,
            User.tiktok,
            User.profession,
            User.employee_business_id,
            Business.id.label("business_id"),
            Business.business_type_id.label("business_type_id"),
            Business.address.label("business_address"),
            distance_expr
        )
        .outerjoin(
            Business,
            or_(
                User.employee_business_id == Business.id,
                User.id == Business.owner_id
            )
        )
        .where(and_(User.id == user_id))
    )

    user = user_stmt.mappings().first()
    counters = await db.get(UserCounters, user.id)

    is_own_profile = user.id == auth_user_id
    is_follow = False

    if not is_own_profile:
        follow_exists = await db.scalar(
            select(exists().where(
                and_(
                    Follow.follower_id == auth_user_id,
                    Follow.followee_id == user_id
                )
            ))
        )
        is_follow = follow_exists

    business_ower = None

    if user.business_id is not None:
        business = await db_get_one(
            db=db,
            model=Business,
            filters={Business.id: user.business_id},
            joins=[joinedload(Business.business_owner)]
        )

        business_ower = UserProfileBusinessOwner(
            id = business.business_owner.id,
            fullname=business.business_owner.fullname,
            username=business.business_owner.username,
            avatar=business.business_owner.avatar,
        )

    is_business_or_employee = user.employee_business_id is not None or business_ower is not None

    schedules = await db_get_all(db,
                                 model=Schedule,
                                 filters={ Schedule.user_id: user_id },
                                 order_by="day_week_index",
                                 descending=False)

    now = datetime.now().astimezone(ZoneInfo('Europe/Bucharest'))

    schedule_map = {}
    for s in schedules:
        if s.start_time and s.end_time:
            schedule_map[s.day_week_index] = (s.start_time, s.end_time)

    today_index = now.weekday()
    start_end_today = schedule_map.get(today_index)

    open_now = False
    closing_time = None
    next_open_day = None
    next_open_time = None

    # Check today
    if start_end_today:
        start_time, end_time = start_end_today

        start_dt = datetime.combine(now.date(), start_time, tzinfo=now.tzinfo)
        end_dt = datetime.combine(now.date(), end_time, tzinfo=now.tzinfo)

        if start_dt <= now <= end_dt:
            open_now = True
            closing_time = end_time.strftime('%H:%M')

    # Find next open day
    if not open_now:
        for i in range(1, 8):
            next_day_index = (today_index + i) % 7
            next_schedule = schedule_map.get(next_day_index)

            if next_schedule:
                next_start_time, _ = next_schedule
                next_date = now + timedelta(days=i)
                weekday_name = next_date.strftime('%A')

                next_open_day = weekday_name
                next_open_time = next_start_time.strftime('%H:%M')
                break

    return UserProfileResponse(
        id=user.id,
        username=user.username,
        fullname=user.fullname,
        avatar=user.avatar,
        bio=user.bio,
        gender=user.gender,
        website=user.website,
        public_email=user.public_email,
        instagram=user.instagram,
        youtube=user.youtube,
        tiktok=user.tiktok,
        business_id=user.business_id,
        business_type_id=user.business_type_id,
        counters=counters,
        profession=user.profession,
        opening_hours=OpeningHours(
            open_now=open_now,
            closing_time=closing_time,
            next_open_day=next_open_day,
            next_open_time=next_open_time
        ),
        is_follow=is_follow,
        business_owner=business_ower,
        is_own_profile=is_own_profile,
        is_business_or_employee=is_business_or_employee,
        distance_km=round(user.distance_km, 1) if user.distance_km else None,
        address=user.business_address
    )

async def update_user_fullname(
        db: DBSession,
        fullname_update: FullNameUpdate,
        auth_user: AuthenticatedUser
) -> UserUpdateResponse:
    auth_user_id = auth_user.id

    user = await db_update(
        db=db,
        model=User,
        update_data=fullname_update,
        filters={ "id": auth_user_id }
    )

    return UserUpdateResponse(
        id=user.id,
        fullname=user.fullname,
        username=user.username,
        bio=user.bio,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        website=user.website,
        public_email=user.public_email,
    )

async def update_user_username(
    db: DBSession,
    username_update: UsernameUpdate,
    auth_user: AuthenticatedUser
) -> UserUpdateResponse:
    auth_user_id = auth_user.id

    user_stmt = await db.execute(
        select(User)
        .where(and_(User.id == auth_user_id))
        .options(joinedload(User.role))
    )

    user = user_stmt.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    user.username = username_update.username
    user.fullname = username_update.username

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserUpdateResponse(
        id=user.id,
        fullname=user.fullname,
        username=user.username,
        bio=user.bio,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        website=user.website,
        public_email=user.public_email,
    )

async def update_user_birthdate(
    db: DBSession,
    birthdate_update: BirthDateUpdate,
    auth_user: AuthenticatedUser
) -> UserUpdateResponse:
    auth_user_id = auth_user.id
    user = await db.get(User, auth_user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    birthdate = birthdate_update.birthdate

    if birthdate is not None:
        user.date_of_birth = date.fromisoformat(birthdate)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserUpdateResponse(
        id=user.id,
        fullname=user.fullname,
        username=user.username,
        bio=user.bio,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        website=user.website,
        public_email=user.public_email,
    )

async def update_user_gender(
    db: DBSession,
    gender_update: GenderUpdate,
    auth_user: AuthenticatedUser
) -> UserUpdateResponse:
    auth_user_id = auth_user.id
    user: User = await db.get(User, auth_user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    user.gender = gender_update.gender
    db.add(user)

    await db.commit()
    await db.refresh(user)

    return UserUpdateResponse(
        id=user.id,
        fullname=user.fullname,
        username=user.username,
        bio=user.bio,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        website=user.website,
        public_email=user.public_email,
    )

async def update_user_bio(
        db: DBSession,
        bio_update: BioUpdate,
        auth_user: AuthenticatedUser
) -> UserUpdateResponse:
    auth_user_id = auth_user.id

    user= await db_update(
        db=db,
        model=User,
        update_data=bio_update,
        filters={ "id": auth_user_id }
    )

    return UserUpdateResponse(
        id=user.id,
        fullname=user.fullname,
        username=user.username,
        bio=user.bio,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        website=user.website,
        public_email=user.public_email,
    )

async def update_user_website(
        db: DBSession,
        website_update: WebsiteUpdate,
        auth_user: AuthenticatedUser
) -> UserUpdateResponse:
    auth_user_id = auth_user.id

    user = await db_update(
        db=db,
        model=User,
        update_data=website_update,
        filters={ "id": auth_user_id }
    )

    return UserUpdateResponse(
        id=user.id,
        fullname=user.fullname,
        username=user.username,
        bio=user.bio,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        website=user.website,
        public_email=user.public_email,
    )

async def update_user_public_email(
        db: DBSession,
        public_email_update: PublicEmailUpdate,
        auth_user: AuthenticatedUser
) -> UserUpdateResponse:
    auth_user_id = auth_user.id

    user = await db_update(
        db=db,
        model=User,
        update_data=public_email_update,
        filters={"id": auth_user_id}
    )

    return UserUpdateResponse(
        id=user.id,
        fullname=user.fullname,
        username=user.username,
        bio=user.bio,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        website=user.website,
        public_email=user.public_email,
    )

async def get_product_durations_by_user_id(db: DBSession, user_id):
    durations_results = await db.execute(select(distinct(Product.duration)).where(Product.user_id == user_id)) #type: ignore
    return [row[0] for row in durations_results]

async def get_user_dashboard_summary_by_id(db: DBSession, user_id: int, start_date: str, end_date:str, all_employees: bool):
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)

    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Start date and end date should use the format - %Y-%m-%d")

    days_diff = end_date_obj - start_date_obj
    previous_start_date = start_date_obj - days_diff
    previous_end_date = end_date_obj - days_diff
    previous_end_date = previous_end_date.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)

    user = await db_get_one(db, model=User, filters={User.id: user_id},
                            joins=[joinedload(User.role), joinedload(User.owner_business).load_only(Business.id)])
    is_super_admin = user.role.name == RoleEnum.SUPER_ADMIN
    is_business = user.role.name == RoleEnum.BUSINESS

    def calculate_dashboard_summary(s_date, e_date, is_bs, is_sa, all_emp, u_id):
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
                    *( [Appointment.user_id == u_id] if not is_sa and not all_emp else []),
                    *( [Appointment.business_id == user.owner_business.id] if all_emp and is_bs else []),
                    Appointment.created_at >= s_date,
                    Appointment.created_at <= e_date,
                    Appointment.is_blocked == False,
                    Appointment.status == AppointmentStatusEnum.FINISHED
                )
            )
            .group_by(User.id)
        )

    current_result = await db.execute(calculate_dashboard_summary(start_date_obj, end_date_obj, is_business, is_super_admin, all_employees, user_id))
    previous_result = await db.execute(calculate_dashboard_summary(previous_start_date, previous_end_date, is_business, is_super_admin, all_employees, user_id))

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

async def get_user_followers_by_user_id(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[UserBaseMinimum]:
   auth_user_id = auth_user.id

   is_follow = (
       select(Follow)
       .where(and_(
           Follow.follower_id == auth_user_id,
           Follow.followee_id == User.id
       ))
       .correlate(User)
       .exists()
   )

   is_business_or_employee = (
       select(Role)
       .where(and_(
           Role.id == User.role_id,
           or_(
               Role.name == RoleEnum.BUSINESS,
               Role.name == RoleEnum.EMPLOYEE
           )
       ))
       .correlate(User)
       .exists()
   )

   followers_query = (
       select(
           User.id,
           User.fullname,
           User.username,
           User.profession,
           User.avatar,
           UserCounters.ratings_average,
           is_follow.label("is_follow"),
           is_business_or_employee.label("is_business_or_employee")
       )
            .join(Follow, Follow.follower_id == User.id)
            .join(UserCounters, UserCounters.user_id == User.id)
            .where(Follow.followee_id == user_id)
        )

   total_count = await db.execute(followers_query)

   followers_query = followers_query.offset((pagination.page - 1) * pagination.limit).limit(pagination.limit)
   followers_result = await db.execute(followers_query)

   count = len(total_count.scalars().all())
   data = followers_result.mappings().all()

   return PaginatedResponse(
       count=count,
       results=data
   )

async def get_user_followings_by_user_id(
        db: DBSession,
        user_id: int,
        pagination: Pagination,
        auth_user: AuthenticatedUser
) -> PaginatedResponse[UserBaseMinimum]:
   auth_user_id = auth_user.id

   is_follow = (
       select(Follow)
       .where(and_(
           Follow.follower_id == auth_user_id,
           Follow.followee_id == User.id
       ))
       .correlate(User)
       .exists()
   )

   is_business_or_employee = (
       select(Role)
       .where(and_(
           Role.id == User.role_id,
           or_(
               Role.name == RoleEnum.BUSINESS,
               Role.name == RoleEnum.EMPLOYEE
           )
       ))
       .correlate(User)
       .exists()
   )

   followings_query = (
       select(
           User.id,
           User.fullname,
           User.username,
           User.profession,
           User.avatar,
           UserCounters.ratings_average,
           is_follow.label("is_follow"),
           is_business_or_employee.label("is_business_or_employee")
       )
           .join(Follow, Follow.followee_id == User.id)
           .join(UserCounters, UserCounters.user_id == User.id)
           .where(Follow.follower_id == user_id)
   )

   total_count = await db.execute(followings_query)
   followings_query = followings_query.offset((pagination.page - 1) * pagination.limit).limit(pagination.limit)

   followings_result = await db.execute(followings_query)

   count = len(total_count.scalars().all())
   data = followings_result.mappings().all()

   return PaginatedResponse(
       count=count,
       results=data
   )

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

    return None