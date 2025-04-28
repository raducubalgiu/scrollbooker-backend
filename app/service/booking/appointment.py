from collections import defaultdict

from fastapi import HTTPException
from datetime import datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo
import pytz #type: ignore
from starlette.requests import Request
from starlette import status
from app.core.crud_helpers import db_create, db_get_one, db_get_all
from app.core.data_utils import utc_to_local
from app.schema.booking.appointment import AppointmentCreate
from app.core.dependencies import DBSession
from app.models import Appointment, Schedule, User, Product
from sqlalchemy import select, and_, or_
from app.core.logger import logger
import random
from collections import defaultdict

async def create_appointment_scheduler(db: DBSession):
    # Get All Clients
    stmt_users = await db.execute(select(User.id).where(User.role_id == 2)) #type: ignore
    all_users_ids = stmt_users.scalars().all()

    all_appointments_stmt = await db.execute(select(Appointment))
    all_appointments = all_appointments_stmt.scalars().all()
    data = []

    for user_id in all_users_ids:
        data.append({
            "user_id": user_id,
            "appointments": [appointment.id for appointment in all_appointments if appointment.customer_id == user_id],
        })

    users_with_low_appointments = sorted(data, key=lambda x: len(x["appointments"]), reverse=True)[:1]

    for user in users_with_low_appointments:
        if len(user["appointments"]) == 0:
            print('Hello World')
        else:
            # Create a new appointment based on the previous one
            random_appointment_id = random.choice(user["appointments"])
            appointment = await db.get(Appointment, random_appointment_id)

            new_start_date = appointment.start_date + timedelta(days=1)
            new_end_date = appointment.end_date + timedelta(days=1)

            # Check if there exists an appointment for next day
            existing_appointment = await db_get_one(db, model=Appointment, filters={
                Appointment.user_id: appointment.user_id,
                Appointment.start_date: new_start_date,
                Appointment.end_date: new_end_date
            }, raise_not_found=False)

            # Check if is in the User Schedule

            # Create a new reservation adding 1 DAY to start_time * end_time
            if not existing_appointment:
                new_appointment = Appointment(
                    start_date=new_start_date,
                    end_date=new_end_date,
                    product_id=appointment.product_id,
                    service_id=appointment.service_id,
                    business_id=appointment.business_id,
                    customer_id=appointment.customer_id,
                    user_id=appointment.user_id
                )

                db.add(new_appointment)
                await db.commit()
                await db.refresh(new_appointment)
                return new_appointment
            else:
                return {"detail": "Could not create any appointment"}
    return {"detail": "Nothing happened!"}


async def create_new_appointment(db: DBSession, appointment_create: AppointmentCreate, request: Request):
    auth_user_id = request.state.user.get("id")
    product = await db_get_one(db, model=Product, filters={Product.id: appointment_create.product_id})

    # TODO: Add Validation for not be able to create appointment in the past

    stmt = await db.execute(
        select(Appointment).where(
            or_(
                and_(
                    Appointment.user_id == product.user_id,
                    Appointment.start_date == appointment_create.start_date
                ),
                and_(Appointment.customer_id == auth_user_id,
                    Appointment.start_date == appointment_create.start_date)
            )
        ))
    is_slot_booked = stmt.scalars().first()

    if is_slot_booked:
        logger.error(f"Business/Employee with id: {product.user_id} already has an appointment starting at: {appointment_create.start_date}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="This slot is already booked")

    return await db_create(db, model=Appointment, create_data=appointment_create, extra_params={
        "customer_id": auth_user_id,
        'user_id': product.user_id,
        'business_id': product.business_id,
        'service_id': product.service_id
    })

async def change_appointment_status(db: DBSession, appointment_id: int, appointment_status: str, request: Request):
    return

async def get_daily_available_slots(db: DBSession, day: str, user_id: int, slot_duration: int):
    slots = {
        "is_closed": False,
        "available_slots": []
    }

    try:
        requested_date = datetime.strptime(day, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Invalid date format. Use YYYY-MM-DD')

    now_utc = datetime.now(timezone.utc)
    today_utc = now_utc.date()
    if requested_date < today_utc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Date must be today or in the future')

    result = await db.execute(
        select(Schedule)
        .where(Schedule.user_id == user_id, Schedule.day_of_week == requested_date.strftime("%A")) #type: ignore
    )
    schedule = result.scalars().first()

    if not schedule.start_time or not schedule.end_time:
        slots["is_closed"] = True
        slots["available_slots"] = []
        return slots

    if not schedule:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='No schedule found for this user on the selected day')

    schedule_start_dt = datetime.combine(requested_date, schedule.start_time)
    schedule_end_dt = datetime.combine(requested_date, schedule.end_time)

    schedule_start_utc = schedule_start_dt.astimezone(timezone.utc)
    schedule_end_utc = schedule_end_dt.astimezone(timezone.utc)

    result = await db.execute(
        select(Appointment.start_date, Appointment.end_date)
        .where(
            Appointment.user_id == user_id, #type: ignore
            Appointment.start_date >= datetime.combine(requested_date, time(0,0), timezone.utc),
            Appointment.start_date < datetime.combine(requested_date + timedelta(days=1), time(0, 0), timezone.utc)
        )
    )
    booked_appointments= result.all()

    booked_slots = set()

    for appointment in booked_appointments:
        start = appointment[0].astimezone(timezone.utc)
        end = appointment[1].astimezone(timezone.utc)
        current = start
        while current < end:
            booked_slots.add(current.isoformat())
            current += timedelta(minutes=slot_duration)

    current_slot = schedule_start_utc

    if requested_date == today_utc:
        next_hour = now_utc.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=slot_duration)
        current_slot = max(schedule_start_utc, next_hour)

    while current_slot < schedule_end_utc:
        slot_start = current_slot
        slot_end = current_slot + timedelta(minutes=slot_duration)
        slot_start_local = await utc_to_local(timezone="Europe/Bucharest", utc_time=str(slot_start.time()))

        if slot_start.isoformat() not in booked_slots:
            slots["available_slots"].append({
                "start_date": slot_start.isoformat(),
                "end_date": slot_end.isoformat(),
                "start_local": slot_start_local
            })
        current_slot = slot_end

    return slots

async def get_calendar_available_slots(db: DBSession, start_date: str, end_date: str, user_id: int, slot_duration: int):
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

    if start_dt > end_dt:
        raise ValueError("start date cannot be after end date")

    calendar = {}

    current_date = start_dt
    while current_date <= end_dt:
        timeslots = await get_daily_available_slots(db, current_date.strftime("%Y-%m-%d"), user_id, slot_duration)
        calendar[current_date.isoformat()] = timeslots
        current_date += timedelta(days=1)

    return calendar

async def get_user_calendar_events(db: DBSession, start_date: str, end_date: str, user_id: int, slot_duration: int, user_timezone: str):
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Create Timezone object
    tz = ZoneInfo(user_timezone)

    # Create Local datetimes
    local_start = datetime.combine(start_date_obj, time.min).replace(tzinfo=tz)
    local_end = datetime.combine(end_date_obj, time.max).replace(tzinfo=tz)

    # Convert to UTC
    start_utc = local_start.astimezone(ZoneInfo('UTC'))
    end_utc = local_end.astimezone(ZoneInfo('UTC'))

    # if start_date_obj > end_date_obj:
    #      raise ValueError("start date cannot be after end date")

    schedules_stmt = select(Schedule).where(Schedule.user_id == user_id) #type: ignore
    schedules_result = await db.execute(schedules_stmt)
    schedules = {schedule.day_of_week: schedule for schedule in schedules_result.scalars().all()}

    appointments_stmt = (select(
        Appointment.start_date,
        Appointment.end_date,
        User.id,
        User.username,
        User.fullname,
        User.avatar,
    )
        .join(User, User.id == Appointment.customer_id) #type: ignore
        .where(
            Appointment.user_id == user_id, # type: ignore
            Appointment.start_date >= start_utc,
            Appointment.end_date <= end_utc
        ))

    appointment_results = await db.execute(appointments_stmt)
    appointments = appointment_results.all()

    # Group appointments by date and slot duration
    grouped_appointments = defaultdict(list)
    for a_start, a_end, customer_id, username, fullname, avatar in appointments:
        appointment_date = a_start.date()
        #start_date = a_start
        # Group by the slot duration
        # while start_date < a_end:
        #     end_date = start_date + timedelta(minutes=slot_duration)
        #     if end_date > a_end:
        #         end_date = a_end
        #     grouped_appointments[appointment_date][start_date].append({
        #         "start_date": start_date,
        #         "end_date": end_date,
        #         "customer": {
        #             "id": customer_id,
        #             "username": username,
        #             "fullname": fullname,
        #             "avatar": avatar
        #         }
        #     })
        #     start_date = end_date
        grouped_appointments[appointment_date].append({
            "start_date": a_start,
            "end_date": a_end,
            "customer": {
                "id": customer_id,
                "username": username,
                "fullname": fullname,
                "avatar": avatar
            }
        })

    slots = []
    min_slot_time = None
    max_slot_time = None
    current_date = start_date_obj

    while current_date <= end_date_obj:
        day_name = current_date.strftime("%A")
        schedule = schedules.get(day_name)

        if not schedule or not schedule.start_time or not schedule.end_time:
            slots.append({
                "date": current_date.isoformat(),
                "is_closed": True,
                "slots": []
            })
        else:
            day_slots = []

            start_time_local = datetime.combine(current_date, schedule.start_time, tzinfo=tz)
            end_time_local = datetime.combine(current_date, schedule.end_time, tzinfo=tz)

            current_slot_start = start_time_local

            day_appointments = sorted(grouped_appointments.get(current_date, []), key=lambda x: x["start_date"])

            a_index = 0
            while current_slot_start < end_time_local:
                current_slot_end = current_slot_start + timedelta(minutes=slot_duration)

                if a_index < len(day_appointments):
                    a = day_appointments[a_index]
                    booked_start_time = a["start_date"].astimezone(tz)
                    booked_end_time = a["end_date"].astimezone(tz)

                    if booked_start_time <= current_slot_start < booked_end_time:
                        slot_start_utc = booked_start_time.astimezone(ZoneInfo('UTC'))
                        slot_end_utc = booked_end_time.astimezone(ZoneInfo('UTC'))

                        day_slots.append({
                            "start_date_locale": booked_start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                            "end_date_locale": booked_end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                            "start_date_utc": slot_start_utc.isoformat(),
                            "end_date_utc": slot_end_utc.isoformat(),
                            "is_booked": True,
                            "customer": a["customer"],
                        })

                        # Update minSlot and maxSlot
                        if min_slot_time is None or current_slot_start < min_slot_time:
                            min_slot_time = current_slot_start
                        if max_slot_time is None or current_slot_end > max_slot_time:
                            max_slot_time = current_slot_end

                        # Move current_slot_start to after the booked appointment
                        current_slot_start = booked_end_time
                        a_index += 1
                        continue

                slot_start_utc = current_slot_start.astimezone(ZoneInfo("UTC"))
                slot_end_utc = current_slot_end.astimezone(ZoneInfo("UTC"))

                day_slots.append({
                    "start_date_locale": current_slot_start.strftime('%Y-%m-%dT%H:%M:%S'),
                    "end_date_locale": current_slot_end.strftime('%Y-%m-%dT%H:%M:%S'),
                    "start_date_utc": slot_start_utc.isoformat(),
                    "end_date_utc": slot_end_utc.isoformat(),
                    "is_booked": False,
                    "customer": None,
                })

                # Update minSlot and maxSlot
                if min_slot_time is None or current_slot_start < min_slot_time:
                    min_slot_time = current_slot_start
                if max_slot_time is None or current_slot_end > max_slot_time:
                    max_slot_time = current_slot_end

                current_slot_start = current_slot_end

            slots.append({
                "date": current_date.isoformat(),
                "is_closed": False,
                "slots": day_slots
            })

        current_date += timedelta(days=1)

    return {
        "min_slot_time": min_slot_time.strftime('%H:%M:%S') if min_slot_time else None,
        "max_slot_time": max_slot_time.strftime('%H:%M:%S') if max_slot_time else None,
        "data": slots
    }






