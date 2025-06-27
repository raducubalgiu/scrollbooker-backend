import calendar
from collections import defaultdict
from fastapi import HTTPException
from datetime import datetime, timedelta, time, timezone, date
from zoneinfo import ZoneInfo

from sqlalchemy.orm import aliased
from starlette.requests import Request
from starlette import status
from core.crud_helpers import db_create, db_get_one
from core.enums.enums import AppointmentStatusEnum, AppointmentChannelEnum
from schema.booking.appointment import AppointmentBlock, AppointmentCancel, AppointmentUnblock, \
    AppointmentCreateOwnClient
from core.dependencies import DBSession
from models import Appointment, Schedule, User, Business, Currency, Product
from sqlalchemy import select, and_, or_, desc, func
from core.logger import logger

async def get_appointments_by_user_id(db: DBSession, page: int, limit: int, as_customer: bool, request: Request):
    # user_id can be the id of the business/customer or the id of the customer
    auth_user_id = request.state.user.get("id")

    query = (select(
        Appointment,
        User.id,
        User.fullname,
        User.username,
        User.avatar,
        User.profession,
        Currency.name
    )
    .outerjoin(Currency, Currency.id == Appointment.currency_id)
    .where(Appointment.is_blocked == False))

    if as_customer:
        query = query.where(Appointment.customer_id == auth_user_id)
        query = query.outerjoin(User, User.id == Appointment.user_id)
    else:
        query = query.where(Appointment.user_id == auth_user_id)
        query = query.outerjoin(User, User.id == Appointment.customer_id)

    query = query.offset((page - 1) * limit).limit(limit).order_by(desc("created_at"))

    appointments_stmt = await db.execute(query)
    count_query = await db.execute(select(func.count()).select_from(query.subquery()))
    count = count_query.scalars().first()
    appointments_result = appointments_stmt.all()

    appointments = []

    for appointment, u_id, u_fullname, u_username, u_avatar, u_profession, curr_name in appointments_result:
        appointments.append({
            "start_date": appointment.start_date,
            "end_date": appointment.end_date,
            "channel": appointment.channel,
            "status": appointment.status,
            "is_customer": True,
            "product": {
                "id": appointment.product_id,
                "name": appointment.product_name,
                "price": appointment.product_full_price,
                "price_with_discount": appointment.product_price_with_discount,
                "discount": appointment.product_discount,
                "currency": curr_name,
                "exchange_rate": appointment.exchange_rate
            },
            "user": {
                "id": u_id,
                "fullname": u_fullname or appointment.customer_fullname,
                "username": u_username,
                "avatar": u_avatar,
                "profession": u_profession
            }
        })

    return {
        "count": count,
        "results": appointments
    }

async def create_new_appointment_own_client(db: DBSession, appointment_create: AppointmentCreateOwnClient, request: Request):
    auth_user_id = request.state.user.get("id")

    if auth_user_id != appointment_create.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have permission to perform this action"
        )

    is_slot_booked_result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.user_id == auth_user_id,
                Appointment.start_date == appointment_create.start_date,
                Appointment.status != AppointmentStatusEnum.CANCELED
            )
        ))
    is_slot_booked = is_slot_booked_result.scalars().first()

    if is_slot_booked:
        logger.error(
            f"Business/Employee with id: {auth_user_id} already has an appointment starting at: {appointment_create.start_date}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="This slot is already booked")

    return await db_create(db, model=Appointment, create_data=appointment_create, extra_params={
        "channel": AppointmentChannelEnum.OWN_CLIENT
    })

async def create_new_blocked_appointment(db: DBSession, appointments_create: list[AppointmentBlock], request: Request):
    auth_user_id = request.state.user.get("id")

    for appointment_create in appointments_create:
        if auth_user_id != appointment_create.user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You do not have permission to perform this action")

        is_slot_booked = await db_get_one(db, model=Appointment, raise_not_found=False, filters={
            Appointment.user_id: auth_user_id,
            Appointment.start_date: appointment_create.start_date,
            Appointment.end_date: appointment_create.end_date
        })

        if is_slot_booked:
            logger.error(
                f"Business/Employee with id: {auth_user_id} already has an appointment starting at: {appointment_create.start_date}, ending at: {appointment_create.end_date}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="This slot is already booked")

        business_result = await db.execute(
            select(Business)
            .join(User, User.id == auth_user_id) #type: ignore
            .where(or_(
                Business.owner_id == User.id,
                User.employee_business_id == Business.id
            ))
        )
        business = business_result.scalar_one_or_none()

        if not business:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Business not found')

        new_appointment = Appointment(
            start_date=appointment_create.start_date,
            end_date=appointment_create.end_date,
            message=appointment_create.message,
            user_id=appointment_create.user_id,
            status=AppointmentStatusEnum.FINISHED,
            channel=AppointmentChannelEnum.OWN_CLIENT,
            business_id=business.id,
            customer_fullname='Blocked',
            service_name='Blocked',
            product_name='Blocked',
            product_full_price=1,
            product_price_with_discount=1,
            product_discount=0,
            currency=None,
            is_blocked=True
        )
        db.add(new_appointment)
    await db.commit()

async def unblock_user_appointment(db: DBSession, appointment_unblock: AppointmentUnblock, request: Request):
    auth_user_id = request.state.user.get("id")

    blocked_appointment = await db_get_one(db, model=Appointment, filters={
        Appointment.start_date: appointment_unblock.start_date,
        Appointment.end_date: appointment_unblock.end_date,
        Appointment.user_id: auth_user_id,
        Appointment.is_blocked: True
    })

    if not blocked_appointment:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Blocked Appointment not found')

    if auth_user_id != blocked_appointment.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You do not have permission to perform this action')

    now_utc = datetime.now(timezone.utc)

    if now_utc > blocked_appointment.start_date:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Appointments from the past can not be edited")

    await db.delete(blocked_appointment)
    await db.commit()

async def cancel_user_appointment(db: DBSession, appointment_cancel: AppointmentCancel, request: Request):
    auth_user_id = request.state.user.get("id")
    appointment = await db.get(Appointment, appointment_cancel.appointment_id)

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Appointment Not Found')

    my_appointment_result = await db.execute(
        select(Appointment)
        .where(and_(
            Appointment.id == appointment_cancel.appointment_id,
            or_(
                Appointment.user_id == auth_user_id,
                Appointment.customer_id == auth_user_id
            )
        ))
    )
    my_appointment = my_appointment_result.scalar_one_or_none()

    if not my_appointment:
        logger.error(f"User id: {auth_user_id} tried to cancel appointment: {appointment_cancel.appointment_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You do not have permission to perform this action')

    appointment.status = AppointmentStatusEnum.CANCELED
    appointment.message = appointment_cancel.message
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)

    return appointment

async def get_business_timezone(db: DBSession, user_id: int):
    business_timezone_result = await db.execute(
        select(Business.timezone)
        .join(User, or_(
            Business.owner_id == User.id,
            Business.id == User.employee_business_id
        ))
        .where(User.id == user_id))  # type: ignore

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

async def get_user_calendar_availability(db: DBSession, month: str, user_id: int):
    business_timezone = await get_business_timezone(db, user_id)
    await validate_date(month, '%Y-%m')

    # Create Timezone object
    tz = ZoneInfo(business_timezone)

    year, month_int = map(int, month.split("-"))
    end_day = calendar.monthrange(year, month_int)[1]

    start_date_obj = date(year, month_int, 1)
    end_date_obj = date(year, month_int, end_day)

    # Create Local datetimes
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

    # Create Local datetimes
    local_start = datetime.combine(start_date_obj, time.min).replace(tzinfo=tz)
    local_end = datetime.combine(end_date_obj, time.max).replace(tzinfo=tz)

    # Convert to UTC
    start_utc = local_start.astimezone(ZoneInfo('UTC'))
    end_utc = local_end.astimezone(ZoneInfo('UTC'))

    schedules_stmt = select(Schedule).where(Schedule.user_id == user_id) #type: ignore
    schedules_result = await db.execute(schedules_stmt)
    schedules = {schedule.day_of_week: schedule for schedule in schedules_result.scalars().all()}

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
            Appointment.id,
            Appointment.start_date,
            Appointment.end_date,
            Appointment.service_name,
            Appointment.product_name,
            Appointment.product_full_price,
            Appointment.product_price_with_discount,
            Appointment.product_discount,
            Appointment.channel,
            Appointment.customer_fullname,
            Appointment.is_blocked,
            Appointment.message,
            Currency.id,
            Currency.name,
            Customer.id.label("customer_id"),
            Customer.fullname.label("customer_fullname"),
            Customer.username.label("customer_username"),
            Customer.avatar.label("customer_avatar")
        )
        .join(User, User.id == Appointment.user_id) #type: ignore
        .outerjoin(Customer, Customer.id == Appointment.customer_id)
        .outerjoin(Currency, Currency.id == Appointment.currency_id)
        .where(
            Appointment.user_id == user_id, # type: ignore
            Appointment.start_date >= start_utc,
            Appointment.end_date <= end_utc,
            #Appointment.status != AppointmentStatusEnum.CANCELED
        ))

    appointment_results = await db.execute(appointments_stmt)
    appointments = appointment_results.all()

    # Group appointments by date and slot duration
    grouped_appointments = defaultdict(list)
    for a_id, a_start, a_end, a_serv_name, a_prod_name, a_prod_full_price, a_prod_price_with_discount, a_prod_discount, a_channel, a_customer_fullname, a_is_blocked, a_message, a_currency_id, a_currency_name, customer_id, customer_fullname, customer_username, customer_avatar in appointments:
        appointment_date = a_start.date()

        grouped_appointments[appointment_date].append({
            "id": a_id,
            "start_date": a_start,
            "end_date": a_end,
            "channel": a_channel,
            "service_name": a_serv_name,
            "is_blocked": a_is_blocked,
            "message": a_message,
            "product": {
                "product_name": a_prod_name,
                "product_full_price": a_prod_full_price,
                "product_price_with_discount": a_prod_price_with_discount,
                "product_discount": a_prod_discount,
            },
            "currency": {
                "id": a_currency_id,
                "name": a_currency_name
            },
            "customer": {
                "id": customer_id,
                "fullname": customer_fullname or a_customer_fullname,
                "username": customer_username,
                "avatar": customer_avatar
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
            slots.append({
                "date": current_date.isoformat(),
                "is_closed": True,
                "slots": []
            })
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


                        day_slots.append({
                            "id": a["id"],
                            "start_date_locale": booked_start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                            "end_date_locale": booked_end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                            "start_date_utc": slot_start_utc.isoformat(),
                            "end_date_utc": slot_end_utc.isoformat(),
                            "is_booked": False if a["is_blocked"] else True,
                            "is_closed": False,
                            "is_blocked": a["is_blocked"],
                            "info": {
                                "currency": a["currency"],
                                "channel": a["channel"],
                                "service_name": a["service_name"],
                                "product": a["product"],
                                "customer": a["customer"],
                                "message": a["message"]
                            }
                        })

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

                day_slots.append({
                    "id": None,
                    "start_date_locale": current_slot_start.strftime('%Y-%m-%dT%H:%M:%S'),
                    "end_date_locale": current_slot_end.strftime('%Y-%m-%dT%H:%M:%S'),
                    "start_date_utc": slot_start_utc.isoformat(),
                    "end_date_utc": slot_end_utc.isoformat(),
                    "is_booked": False,
                    "is_closed": is_closed,
                    "is_blocked": False,
                    "info": None,
                })

                # Update minSlot and maxSlot
                if min_slot_time is None or current_slot_start < min_slot_time:
                    min_slot_time = current_slot_start
                if max_slot_time is None or current_slot_end > max_slot_time:
                    max_slot_time = current_slot_end

                current_slot_start = current_slot_end

            if day_slots and end_time_local > max_slot_time:
                max_slot_time = end_time_local

            if all(slot["is_booked"] or slot["is_closed"] for slot in day_slots):
                is_booked_day = True
            else:
                is_booked_day = False

            slots.append({
                "date": current_date.isoformat(),
                "is_booked": is_booked_day,
                "is_closed": False,
                "slots": day_slots
            })
        current_date += timedelta(days=1)

    return {
        "min_slot_time": min_slot_time.strftime('%H:%M:%S') if min_slot_time else None,
        "max_slot_time": max_slot_time.strftime('%H:%M:%S') if max_slot_time else None,
        "data": slots
    }






