from fastapi import HTTPException
from datetime import datetime, timedelta, time, timezone
import pytz #type: ignore
from starlette.requests import Request
from starlette import status
from app.core.crud_helpers import db_create, db_get_one
from app.core.data_utils import utc_to_local
from app.schema.booking.appointment import AppointmentCreate
from app.core.dependencies import DBSession
from app.models import Appointment, Schedule, User, Product
from sqlalchemy import select, and_, or_
from app.core.logger import logger
import random

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


async def create_new_appointment(db: DBSession, appointment: AppointmentCreate, request: Request):
    auth_user_id = request.state.user.get("id")
    product = await db_get_one(db, model=Product, filters={Product.id: appointment.product_id})

    stmt = await db.execute(
        select(Appointment).where(
            or_(
                and_(
                    Appointment.user_id == product.user_id,
                    Appointment.start_date == appointment.start_date
                ),
                and_(Appointment.customer_id == auth_user_id,
                    Appointment.start_date == appointment.start_date)
            )
        ))
    is_slot_booked = stmt.scalars().first()

    if is_slot_booked:
        logger.error(f"Business/Employee with id: {product.user_id} already has an appointment starting at: {appointment.start_date}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="This slot is already booked")

    return await db_create(db, model=Appointment, create_data=appointment, extra_params={
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

async def get_calendar_available_slots(db: DBSession, start_date: str, end_date: str, user_id: int):
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

    if start_dt > end_dt:
        raise ValueError("start date cannot be after end date")

    calendar = {}

    current_date = start_dt
    while current_date <= end_dt:
        timeslots = await get_daily_available_slots(db, current_date.strftime("%Y-%m-%d"), user_id)
        calendar[current_date.isoformat()] = timeslots
        current_date += timedelta(days=1)
    return calendar
