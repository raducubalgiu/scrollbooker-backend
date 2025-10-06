from fastapi import HTTPException, Response, Request, status
from datetime import datetime
from core.enums.appointment_status_enum import AppointmentStatusEnum
from schema.booking.appointment import AppointmentBlock, AppointmentCancel, AppointmentScrollBookerCreate, AppointmentResponse, \
    AppointmentOwnClientCreate
from core.dependencies import DBSession
from models import Appointment, User, Service, Product
from sqlalchemy import select, and_, or_
from core.logger import logger
from service.booking.business import get_business_by_user_id

async def _is_slot_booked(
        db: DBSession,
        user_id: int,
        auth_user_id: int,
        start_date: datetime,
        end_date: datetime,
        is_scroll_booker: bool
) -> AppointmentResponse:
    conditions = [
        Appointment.user_id == user_id,
        Appointment.status != AppointmentStatusEnum.CANCELED,
        Appointment.start_date < end_date,
        Appointment.end_date > start_date,
    ]

    if is_scroll_booker:
        conditions.append(Appointment.customer_id == auth_user_id)

    is_booked = await db.scalar(
        select(Appointment.id).where(and_(*conditions)).limit(1)
    )

    if is_booked:
        logger.error(
            f"Business/Employee with id: {auth_user_id} already has an appointment starting at: {start_date}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="This slot is already booked")

    return is_booked

async def create_new_scroll_booker_appointment(
        db: DBSession,
        appointment_create: AppointmentScrollBookerCreate,
        request: Request
) -> AppointmentResponse:
    try:
        async with db.begin():
            auth_user_id = request.state.user.get("id")

            # Check Appointment Availability
            await _is_slot_booked(
                db=db,
                user_id=appointment_create.user_id,
                auth_user_id=auth_user_id,
                start_date=appointment_create.start_date,
                end_date=appointment_create.end_date,
                is_scroll_booker=True
            )

            business = await get_business_by_user_id(db, appointment_create.user_id)
            auth_user = await db.get(User, auth_user_id)

            if not auth_user:
                logger.error(f"Customer with id: {auth_user.id} not found")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Customer not found")

            service = await db.get(Service, appointment_create.service_id)

            if not service:
                logger.error(f"Service with id: {service.id} not found")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Service not found")

            product = await db.get(Product, appointment_create.product_id)

            if not service:
                logger.error(f"Product with id: {product.id} not found")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Product not found")

            appointment = Appointment(
                **appointment_create.model_dump(),
                service_name=service.name,
                business_id=business.id,
                customer_id=auth_user.id,
                customer_fullname=auth_user.fullname,
                product_name=product.name,
                product_full_price=product.price,
                product_price_with_discount=product.price_with_discount,
                product_duration=product.duration,
                product_discount=product.discount
            )

            db.add(appointment)
            await db.flush()
            await db.refresh(appointment)

        return appointment
    except Exception as e:
        logger.error(f"Something went wrong. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )

async def create_new_own_client_appointment(
        db: DBSession,
        appointment_create: AppointmentOwnClientCreate,
        request: Request
) -> Response:
    try:
        async with db.begin():
            auth_user_id = request.state.user.get("id")

            await _is_slot_booked(
                db=db,
                user_id=auth_user_id,
                auth_user_id=auth_user_id,
                start_date=appointment_create.start_date,
                end_date=appointment_create.end_date,
                is_scroll_booker=False
            )

            business = await get_business_by_user_id(db, auth_user_id)

            new_appointment = Appointment(
                **appointment_create.model_dump(),
                user_id=auth_user_id,
                business_id=business.id,
            )
            db.add(new_appointment)

        return Response(status_code=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Something went wrong. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )

async def create_new_blocked_appointment(
        db: DBSession,
        appointments_create: AppointmentBlock,
        request: Request
) -> Response:
    try:
        async with db.begin():
            auth_user_id = request.state.user.get("id")

            for app_create in appointments_create.slots:
                await _is_slot_booked(
                    db=db,
                    user_id=auth_user_id,
                    auth_user_id=auth_user_id,
                    start_date=app_create.start_date,
                    end_date=app_create.end_date,
                    is_scroll_booker=False
                )

                business = await get_business_by_user_id(db, auth_user_id)

                new_appointment = Appointment(
                    **app_create.model_dump(),
                    message=appointments_create.message,
                    user_id=auth_user_id,
                    business_id=business.id,
                )
                db.add(new_appointment)

        return Response(status_code=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Something went wrong. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )

async def cancel_user_appointment(
        db: DBSession,
        appointment_cancel: AppointmentCancel,
        request: Request
) -> Response:
    try:
        async with db.begin():
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

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Something went wrong. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Something went wrong'
        )





