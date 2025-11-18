from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, Response, status
from datetime import datetime, timezone
from core.enums.appointment_status_enum import AppointmentStatusEnum
from schema.booking.appointment import AppointmentBlock, AppointmentCancel, AppointmentScrollBookerCreate, \
    AppointmentOwnClientCreate
from core.dependencies import DBSession, AuthenticatedUser
from models import Appointment, User, Product, AppointmentProduct, UserCurrency
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
) -> bool:
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

    return True if is_booked else False

async def create_new_scroll_booker_appointment(
        db: DBSession,
        appointment_create: AppointmentScrollBookerCreate,
        auth_user: AuthenticatedUser
):
    async with db.begin():
        auth_user_id = auth_user.id
        product_ids: list[int] = appointment_create.product_ids
        payment_currency_id: int = appointment_create.payment_currency_id

        # Check Products - Unique Ids
        if len(product_ids) != len(set(product_ids)):
            sames_ids = sorted({x for x in product_ids if product_ids.count(x) > 1})
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"The products must be unique. Duplicates: {sames_ids}")

        # Get auth_user (Customer) & Business
        business = await get_business_by_user_id(db, appointment_create.user_id)
        auth_user = await db.get(User, auth_user_id)

        if not auth_user:
            logger.error(f"Customer with id: {auth_user.id} not found")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Customer not found")

        # Check Appointment Availability
        is_booked = await _is_slot_booked(
            db=db,
            user_id=appointment_create.user_id,
            auth_user_id=auth_user_id,
            start_date=appointment_create.start_date,
            end_date=appointment_create.end_date,
            is_scroll_booker=True
        )

        if is_booked:
            logger.error(
                f"Business/Employee with id: {auth_user_id} already has an appointment starting at: {appointment_create.start_date}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="This slot is already booked")

        # Fetch products
        products_query = await db.execute(
            select(
                Product.id,
                Product.service_id,
                Product.business_id,
                Product.name,
                Product.price,
                Product.price_with_discount,
                Product.discount,
                Product.duration,
                Product.currency_id
            )
            .where(Product.id.in_(product_ids))
        )
        products = products_query.all()

        # Check if all products exists
        found_ids = {p.id for p in products}
        missing = [pid for pid in product_ids if pid not in found_ids]
        if missing:
            logger.error(f"Some of the products not found. Missing: {missing}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Some of the products was not found")

        # Check if all products belongs to Business
        for p in products:
            if p.business_id != business.id:
                logger.error(f"Product with id: {p.id} does not belong Business with id: {business.id}.")
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail="Product does not belong to Business")

        # Validate currency
        allowed_currency_ids = (
            await db.execute(
                select(UserCurrency.currency_id)
                .where(UserCurrency.user_id == appointment_create.user_id)
            )
        ).scalars().all()

        if payment_currency_id not in allowed_currency_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Business/Employees not does accept this currency")

        # # Get Currency Name
        # target_minor_units = (
        #     await db.execute(
        #         select(Currency.name)
        #         .where(Currency.id == payment_currency_id)
        #     )
        # ).scalar_one()

        # Calculate totals
        exchange_rate_timestamp = datetime.now(timezone.utc)
        any_converted = False

        total_price: Decimal = Decimal("0")
        total_price_with_discount: Decimal = Decimal("0")
        total_duration: int = 0

        link_models: list[AppointmentProduct] = []

        for p in products:
            price: Decimal = p.price
            price_with_discount: Decimal = p.price_with_discount
            total_duration += p.duration

            if p.currency_id == payment_currency_id:
                exchange_rate: Optional[Decimal] = None
                converted_price = price
                converted_price_with_discount = price_with_discount
            else:
                # Convert Price -- Should complete
                any_converted = True

            total_price += converted_price
            total_price_with_discount += converted_price_with_discount

            link_models.append(
                AppointmentProduct(
                    appointment_id=None,
                    product_id=p.id,
                    name=p.name,
                    price=p.price,
                    price_with_discount=p.price_with_discount,
                    discount=p.discount,
                    duration=p.duration,
                    currency_id=p.currency_id,
                    converted_price_with_discount=converted_price_with_discount,
                    exchange_rate=exchange_rate
                )
            )

        discount_value = total_price - total_price_with_discount
        total_discount = (discount_value / total_price) * 100

        # Create Appointment
        appointment = Appointment(
            start_date=appointment_create.start_date,
            end_date=appointment_create.end_date,
            user_id=appointment_create.user_id,
            business_id=business.id,
            customer_id=auth_user.id,
            customer_fullname=auth_user.fullname,
            total_price=total_price,
            total_price_with_discount=total_price_with_discount,
            total_discount=total_discount,
            total_duration=total_duration,
            payment_currency_id=payment_currency_id,
            exchange_rate_source=("BNR" if any_converted else None),
            exchange_rate_timestamp=exchange_rate_timestamp if exchange_rate_timestamp else None
        )
        db.add(appointment)
        await db.flush()

        # Link Appointment products
        for ap in link_models:
            ap.appointment_id = appointment.id
        db.add_all(link_models)

        await db.refresh(appointment)

    return appointment

async def create_new_own_client_appointment(
        db: DBSession,
        appointment_create: AppointmentOwnClientCreate,
        auth_user: AuthenticatedUser
) -> Response:
    try:
        async with db.begin():
            auth_user_id = auth_user.id

            is_booked = await _is_slot_booked(
                db=db,
                user_id=auth_user_id,
                auth_user_id=auth_user_id,
                start_date=appointment_create.start_date,
                end_date=appointment_create.end_date,
                is_scroll_booker=False
            )

            if is_booked:
                logger.error(
                    f"Business/Employee with id: {auth_user_id} already has an appointment starting at: {appointment_create.start_date}")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="This slot is already booked")

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
        auth_user: AuthenticatedUser
) -> Response:
    try:
        async with db.begin():
            auth_user_id = auth_user.id

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
        auth_user: AuthenticatedUser
) -> Response:
    async with db.begin():
        auth_user_id = auth_user.id
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





