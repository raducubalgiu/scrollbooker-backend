from collections import defaultdict
from typing import Optional

from fastapi import HTTPException, Request, status
from datetime import datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import aliased, joinedload

from core.crud_helpers import PaginatedResponse
from core.enums.appointment_status_enum import AppointmentStatusEnum
from core.enums.role_enum import RoleEnum
from schema.booking.appointment import UserAppointmentResponse, AppointmentProduct, AppointmentBusiness, \
    CalendarEventsSlot, CalendarEventsInfo, \
    CalendarEventsResponse, CalendarEventsDay, CalendarEventsCustomer
from core.dependencies import DBSession
from models import Appointment, Schedule, User, Business, Currency, Product
from schema.user.user import UserBaseMinimum
from service.booking.business import get_business_by_user_id

async def get_appointments_by_user_id(db: DBSession, page: int, limit: int, request: Request, as_customer: Optional[bool] = None):
    auth_user_id = request.state.user.get("id")

    user_stmt = await db.execute(
        select(User)
        .where(User.id == auth_user_id)
        .options(joinedload(User.role))
    )
    user = user_stmt.scalar_one_or_none()

    is_filter_allowed = user.role.name is RoleEnum.EMPLOYEE

    customer_user = aliased(User)
    provider_user = aliased(User)

    query = (
        select(
            Appointment,
            customer_user.id, customer_user.fullname, customer_user.username, customer_user.avatar, customer_user.profession,
            provider_user.id, provider_user.fullname, provider_user.username, provider_user.avatar, provider_user.profession,
            Currency.name
        )
        .join(customer_user, Appointment.customer_id == customer_user.id)
        .join(provider_user, Appointment.user_id == provider_user.id)
        .outerjoin(Product, Product.id == Appointment.product_id)
        .join(Currency, Currency.id == Appointment.currency_id)
    )

    conditions = [Appointment.is_blocked == False]

    if is_filter_allowed and as_customer is not None:
        if as_customer:
            conditions.append(Appointment.customer_id == auth_user_id)
        else:
            conditions.append(Appointment.user_id == auth_user_id)
    else:
        conditions.append(
            or_(
                Appointment.customer_id == auth_user_id,
                Appointment.user_id == auth_user_id
            )
        )

    query = query.where(and_(*conditions))
    query = query.order_by(desc(Appointment.created_at)).offset((page - 1) * limit).limit(limit)

    total_count = await db.execute(select(func.count()).select_from(query.subquery()))
    count = total_count.scalars().first()

    result = await db.execute(query)
    rows = result.all()

    appointments = []

    for (appointment,
         c_id, c_fullname, c_username, c_avatar, c_prof,
         p_id, p_fullname, p_username, p_avatar, p_prof,
         curr_name
    ) in rows:
        is_customer = appointment.customer_id == auth_user_id
        business = await get_business_by_user_id(db, p_id)

        appointments.append(
            UserAppointmentResponse(
                id=appointment.id,
                start_date=appointment.start_date,
                end_date=appointment.end_date,
                channel=appointment.channel,
                status=appointment.status,
                is_customer=is_customer,
                message=appointment.message,
                product=AppointmentProduct(
                    id=appointment.product_id,
                    name=appointment.product_name,
                    price=appointment.product_full_price,
                    price_with_discount=appointment.product_price_with_discount,
                    duration=appointment.product_duration,
                    discount=appointment.product_discount,
                    currency=curr_name,
                    exchange_rate=appointment.exchange_rate
                ),
                user=UserBaseMinimum(
                    id= p_id if is_customer else c_id,
                    fullname= p_fullname if is_customer else c_fullname,
                    username= p_username if is_customer else c_username,
                    avatar= p_avatar if is_customer else c_avatar,
                    profession= p_prof if is_customer else c_prof
                ),
                business=AppointmentBusiness(
                    address=business.address,
                    coordinates=business.coordinates
                )
            )
        )

    return PaginatedResponse(
        count=count,
        results=appointments
    )

async def get_appointments_number_by_user_id(db: DBSession, request: Request):
    auth_user_id = request.state.user.get("id")

    stmt = (
        select(func.count())
        .select_from(Appointment)
        .where(and_(
                or_(
                    Appointment.customer_id == auth_user_id,
                    Appointment.user_id == auth_user_id
                ),
                Appointment.status != AppointmentStatusEnum.FINISHED,
                Appointment.status != AppointmentStatusEnum.CANCELED
            )
        )
    )
    result = await db.execute(stmt)

    return result.scalar() or 0

async def get_business_timezone(db: DBSession, user_id: int):
    business_timezone_result = await db.execute(
        select(Business.timezone)
        .join(User, or_(
            Business.owner_id == User.id,
            Business.id == User.employee_business_id
        ))
        .where(User.id == user_id))

    business_timezone = business_timezone_result.scalar_one_or_none()

    if not business_timezone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Business Timezone Not Found')

    return business_timezone

async def validate_date(desired_date: str, desired_format: str):
    try:
        datetime.strptime(desired_date, desired_format).date()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid date format. Use {desired_format}")

async def get_daily_available_slots(db: DBSession, day: str, user_id: int, slot_duration: int):
    business_timezone = await get_business_timezone(db, user_id)
    await validate_date(day, '%Y-%m-%d')

    # Create Timezone Object
    tz = ZoneInfo(business_timezone)

    day_obj = datetime.strptime(day, "%Y-%m-%d").date()
    day_local = datetime.combine(day_obj, time.min).replace(tzinfo=tz)

    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(ZoneInfo(business_timezone))

    if day_local.date() < now_local.date():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Date must be today or in the future')

    slots = {"is_closed": False, "available_slots": []}

    result = await db.execute(
        select(Schedule)
        .where(
            and_(
                Schedule.user_id == user_id,
                Schedule.day_of_week == day_local.strftime("%A")
            )
        )
    )
    schedule = result.scalars().first()

    if not schedule.start_time or not schedule.end_time:
        slots["is_closed"] = True
        slots["available_slots"] = []
        return slots

    if not schedule:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='No schedule found for this user on the selected day')

    schedule_start_dt = datetime.combine(day_obj, schedule.start_time).replace(tzinfo=tz)
    schedule_end_dt = datetime.combine(day_obj, schedule.end_time).replace(tzinfo=tz)

    schedule_start_utc = schedule_start_dt.astimezone(ZoneInfo('UTC'))
    schedule_end_utc = schedule_end_dt.astimezone(ZoneInfo('UTC'))

    result = await db.execute(
        select(Appointment.start_date, Appointment.end_date)
        .where(and_(
            Appointment.user_id == user_id,
            Appointment.start_date >= schedule_start_utc,
            Appointment.start_date < schedule_end_utc,
            Appointment.status != AppointmentStatusEnum.CANCELED
        ))
    )
    booked_appointments = result.all()

    booked_slots = set()

    for appointment in booked_appointments:
        start = appointment[0].astimezone(timezone.utc)
        end = appointment[1].astimezone(timezone.utc)
        current = start
        while current < end:
            booked_slots.add(current.isoformat())
            current += timedelta(minutes=slot_duration)

    current_slot = schedule_start_utc

    if day_local.date() == now_local.date():
        next_hour = now_utc.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=slot_duration)
        current_slot = max(schedule_start_utc, next_hour)

    while current_slot < schedule_end_utc:
        slot_start = current_slot
        slot_end = current_slot + timedelta(minutes=slot_duration)

        if slot_start.isoformat() not in booked_slots:
            slots["available_slots"].append({
                "start_date_utc": slot_start.isoformat(),
                "end_date_utc": slot_end.isoformat(),
                "start_date_locale": slot_start.astimezone(ZoneInfo(business_timezone)).strftime('%Y-%m-%dT%H:%M:%S'),
                "end_date_locale": slot_end.astimezone(ZoneInfo(business_timezone)).strftime('%Y-%m-%dT%H:%M:%S'),
            })
        current_slot = slot_end

    return slots

async def get_user_calendar_availability(db: DBSession, start_date: str, end_date: str, user_id: int):
    business_timezone = await get_business_timezone(db, user_id)
    #await validate_date(month, '%Y-%m')

    # Create Timezone object
    tz = ZoneInfo(business_timezone)

    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Create Local datetime
    local_start = datetime.combine(start_date_obj, time.min).replace(tzinfo=tz)
    local_end = datetime.combine(end_date_obj, time.max).replace(tzinfo=tz)

    # Convert to UTC
    start_utc = local_start.astimezone(ZoneInfo('UTC'))
    end_utc = local_end.astimezone(ZoneInfo('UTC'))

    schedules_stmt = select(Schedule).where(Schedule.user_id == user_id)  # type: ignore
    schedules_result = await db.execute(schedules_stmt)
    schedules = {schedule.day_of_week: schedule for schedule in schedules_result.scalars().all()}

    appointments_stmt = (select(
        Appointment.start_date,
        Appointment.end_date,
    )
    .join(User, User.id == Appointment.user_id)  # type: ignore
    .where(
        Appointment.user_id == user_id,  # type: ignore
        Appointment.start_date >= start_utc,
        Appointment.end_date <= end_utc,
        Appointment.status != AppointmentStatusEnum.CANCELED
    ))

    appointment_results = await db.execute(appointments_stmt)
    appointments = appointment_results.all()

    grouped_appointments = defaultdict(list)
    for start, end in appointments:
        grouped_appointments[start.date()].append((start, end))

    available_days = []
    current_date = start_date_obj

    while current_date <= end_date_obj:
        day_name = current_date.strftime("%A")
        schedule = schedules.get(day_name)

        if schedule and schedule.start_time and schedule.end_time:
            schedule_start = datetime.combine(current_date, schedule.start_time, tzinfo=tz)
            schedule_end = datetime.combine(current_date, schedule.end_time, tzinfo=tz)

            total_schedule_duration = (schedule_end - schedule_start).total_seconds()

            # Merge overlapping appointments for the day
            day_a = sorted(grouped_appointments.get(current_date, []), key=lambda x: x[0])
            merged = []
            for a_start, a_end in day_a:
                if not merged or a_start > merged[-1][1]:
                    merged.append([a_start, a_end])
                else:
                    merged[-1][1] = max(merged[-1][1], a_end)

            total_booked = sum((min(schedule_end, end) - max(schedule_start, start)).total_seconds()
                               for start, end in merged if start < schedule_end and end > schedule_start)

            if total_booked < total_schedule_duration:
                available_days.append(current_date.isoformat())

        current_date += timedelta(days=1)

    return available_days

async def get_user_calendar_events(db: DBSession, start_date: str, end_date: str, user_id: int, slot_duration: int):
    business_timezone = await get_business_timezone(db, user_id)
    await validate_date(start_date, "%Y-%m-%d")
    await validate_date(end_date, "%Y-%m-%d")

    # Create Timezone object
    tz = ZoneInfo(business_timezone)

    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Create Local date times
    local_start = datetime.combine(start_date_obj, time.min).replace(tzinfo=tz)
    local_end = datetime.combine(end_date_obj, time.max).replace(tzinfo=tz)

    # Convert to UTC
    start_utc = local_start.astimezone(ZoneInfo('UTC'))
    end_utc = local_end.astimezone(ZoneInfo('UTC'))

    schedules_stmt = select(Schedule).where(Schedule.user_id == user_id)
    schedules_result = await db.execute(schedules_stmt)
    schedules = { schedule.day_of_week: schedule for schedule in schedules_result.scalars().all() }

    global_start_time = time.max
    global_end_time = time.min

    for schedule in schedules.values():
        if schedule.start_time and schedule.start_time < global_start_time:
            global_start_time = schedule.start_time
        if schedule.end_time and schedule.end_time > global_end_time:
            global_end_time = schedule.end_time

    Customer = aliased(User)

    appointments_stmt = (
        select(
            Appointment,
            Currency.id,
            Currency.name,
            Customer.id.label("c_id"),
            Customer.fullname.label("c_fullname"),
            Customer.username.label("c_username"),
            Customer.avatar.label("c_avatar")
        )
        .join(User, User.id == Appointment.user_id)
        .outerjoin(Customer, Customer.id == Appointment.customer_id)
        .outerjoin(Currency, Currency.id == Appointment.currency_id)
        .where(
            and_(
                Appointment.user_id == user_id,
                Appointment.start_date >= start_utc,
                Appointment.end_date <= end_utc,
                Appointment.status != AppointmentStatusEnum.CANCELED
            )
        ))

    appointment_results = await db.execute(appointments_stmt)
    appointments = appointment_results.all()

    # Group appointments by date and slot duration
    grouped_appointments = defaultdict(list)
    for appointment, currency_id, currency_name, c_id, c_fullname, c_username, c_avatar in appointments:
        appointment_date = appointment.start_date.date()

        grouped_appointments[appointment_date].append({
            "id": appointment.id,
            "start_date": appointment.start_date,
            "end_date": appointment.end_date,
            "channel": appointment.channel,
            "service_name": appointment.service_name,
            "is_blocked": appointment.is_blocked,
            "message": appointment.message,
            "product": {
                "product_name": appointment.product_name,
                "product_full_price": appointment.product_full_price,
                "product_price_with_discount": appointment.product_price_with_discount,
                "product_discount": appointment.product_discount,
            },
            "currency": {
                "id": currency_id,
                "name": currency_name
            },
            "customer": {
                "id": c_id,
                "fullname": c_fullname or appointment.customer_fullname,
                "username": c_username,
                "avatar": c_avatar
            }
        })

    slots = []
    min_slot_time = None
    max_slot_time = None
    current_date = start_date_obj

    while current_date <= end_date_obj:
        day_name = current_date.strftime("%A")
        schedule = schedules.get(day_name)
        is_booked_day = True

        if not schedule or not schedule.start_time or not schedule.end_time:
            slots.append(
                CalendarEventsDay(
                    day=current_date.isoformat(),
                    is_booked=True,
                    is_closed=False,
                    slots=[]
                )
            )
        else:
            day_slots = []

            day_start_time = schedule.start_time
            day_end_time = schedule.end_time

            start_time_local = datetime.combine(current_date, global_start_time, tzinfo=tz)
            end_time_local = datetime.combine(current_date, global_end_time, tzinfo=tz)
            current_slot_start = start_time_local

            day_appointments = sorted(grouped_appointments.get(current_date, []), key=lambda x: x["start_date"])

            a_index = 0
            while current_slot_start < end_time_local:
                current_slot_end = current_slot_start + timedelta(minutes=slot_duration)

                if current_slot_end > end_time_local:
                    break

                is_within_schedule = day_start_time <= current_slot_start.time() < day_end_time

                if is_within_schedule and a_index < len(day_appointments):
                    a = day_appointments[a_index]
                    booked_start_time = a["start_date"].astimezone(tz)
                    booked_end_time = a["end_date"].astimezone(tz)

                    if current_slot_start < booked_end_time and current_slot_end > booked_start_time:
                        slot_start_utc = booked_start_time.astimezone(ZoneInfo('UTC'))
                        slot_end_utc = booked_end_time.astimezone(ZoneInfo('UTC'))

                        day_slots.append(
                            CalendarEventsSlot(
                                id=a["id"],
                                start_date_locale=booked_start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                                end_date_locale=booked_end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                                start_date_utc=slot_start_utc.isoformat(),
                                end_date_utc=slot_end_utc.isoformat(),
                                is_booked=False if a["is_blocked"] else True,
                                is_closed=False,
                                is_blocked=a["is_blocked"],
                                info=CalendarEventsInfo(
                                    currency=None if a["is_blocked"] else a["currency"],
                                    channel=a["channel"],
                                    service_name=a["service_name"],
                                    product=a["product"],
                                    customer=None if a["is_blocked"] else CalendarEventsCustomer(
                                        id=a["customer"]["id"],
                                        fullname=a["customer"]["fullname"],
                                        username=a["customer"]["username"],
                                        avatar=a["customer"]["avatar"]
                                    ),
                                    message=a["message"]
                                )
                            )
                        )

                        # Update minSlot and maxSlot
                        if min_slot_time is None or booked_start_time < min_slot_time:
                            min_slot_time = booked_start_time
                        if max_slot_time is None or booked_end_time > max_slot_time:
                            max_slot_time = booked_end_time

                        # Move current_slot_start to after the booked appointment
                        current_slot_start = booked_end_time
                        a_index += 1
                        continue

                slot_start_utc = current_slot_start.astimezone(ZoneInfo("UTC"))
                slot_end_utc = current_slot_end.astimezone(ZoneInfo("UTC"))

                is_closed = not is_within_schedule
                day_appointments = grouped_appointments[current_slot_start.date()]

                day_slots.append(
                    CalendarEventsSlot(
                        id=None,
                        start_date_locale=current_slot_start.strftime('%Y-%m-%dT%H:%M:%S'),
                        end_date_locale=current_slot_end.strftime('%Y-%m-%dT%H:%M:%S'),
                        start_date_utc=slot_start_utc.isoformat(),
                        end_date_utc=slot_end_utc.isoformat(),
                        is_booked=False,
                        is_closed=is_closed,
                        is_blocked=False,
                        info=None
                    )
                )

                # Update minSlot and maxSlot
                if min_slot_time is None or current_slot_start < min_slot_time:
                    min_slot_time = current_slot_start
                if max_slot_time is None or current_slot_end > max_slot_time:
                    max_slot_time = current_slot_end

                current_slot_start = current_slot_end

            if day_slots and end_time_local > max_slot_time:
                max_slot_time = end_time_local

            if all(slot.is_booked or slot.is_closed for slot in day_slots):
                is_booked_day = True
            else:
                is_booked_day = False

            slots.append(
                CalendarEventsDay(
                    day=current_date.isoformat(),
                    is_booked=is_booked_day,
                    is_closed=False,
                    slots=day_slots
                )
            )

        current_date += timedelta(days=1)

    return CalendarEventsResponse(
        min_slot_time=min_slot_time.strftime('%Y-%m-%dT%H:%M:%S') if min_slot_time else None,
        max_slot_time=max_slot_time.strftime('%Y-%m-%dT%H:%M:%S') if max_slot_time else None,
        days=slots
    )