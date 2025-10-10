from fastapi import HTTPException, Response, Request, status
from sqlalchemy.orm import joinedload
from sqlalchemy import select, and_, delete
from core.crud_helpers import db_create, db_get_one
from core.dependencies import DBSession
from core.enums.employment_requests_status_enum import EmploymentRequestsStatusEnum
from core.enums.notification_type import NotificationTypeEnum
from core.enums.role_enum import RoleEnum
from models import EmploymentRequest, Business, User, Role, Notification, Profession, Schedule
from schema.booking.employment_request import EmploymentRequestCreate, EmploymentRequestUpdate
from core.logger import logger
import calendar

from service.booking.business import get_business_by_user_id

async def get_employment_requests_by_user_id(db: DBSession, user_id: int, request: Request):
    auth_user_id = request.state.user.get("id")

    business = await get_business_by_user_id(db, auth_user_id)
    user = await db_get_one(db, model=User, filters={User.id: user_id}, joins=[joinedload(User.role)])

    if not business:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Business not found')

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='User not found')

    if business.owner_id is not user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You do not have permission to perform this action')

    stmt = (
        select(EmploymentRequest)
        .where(
            and_(
                EmploymentRequest.employer_id == user.id,
                EmploymentRequest.status == EmploymentRequestsStatusEnum.PENDING
            )
        )
        .options(
            joinedload(EmploymentRequest.employer),
            joinedload(EmploymentRequest.employee),
            joinedload(EmploymentRequest.profession)
        )
    )

    result = await db.execute(stmt)
    employment_requests = result.scalars().all()

    return employment_requests

async def create_employment_request(db: DBSession, employment_create: EmploymentRequestCreate,  request: Request):
    auth_user_id = request.state.user.get("id")

    business = await db_get_one(
        db=db,
        model=Business,
        filters={Business.owner_id: auth_user_id},
        raise_not_found=False
    )
    profession = await db_get_one(
        db=db,
        model=Profession,
        filters={Profession.id: employment_create.profession_id}
    )

    if not business:
        logger.error(f"Business with ID: {auth_user_id} doesn't have the Business defined")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='You do not have permission to perform this action')

    try :
        employment_request = await db_create(
            db=db,
            model=EmploymentRequest,
            create_data=employment_create,
            extra_params={
                'employer_id': auth_user_id,
                'business_id': business.id
            })

        notification = Notification(
            type="employment_request",
            sender_id=auth_user_id,
            receiver_id=employment_create.employee_id,
            data={
                "employment_request_id": employment_request.id,
                "profession_id": profession.id,
                "profession_name": profession.name
            },
            message="Employment Request Sent By Business"
        )
        db.add(notification)
        await db.commit()

    except Exception as e:
        logger.error(f"The employment request sent by employer_id: {auth_user_id} to user id: {employment_create.employee_id} could not be saved. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')

async def respond_employment_request(
        db: DBSession,
        employment_request_id: int,
        employment_update: EmploymentRequestUpdate,
        request: Request
) -> Response:
    try:
        async with db.begin():
            auth_user_id = request.state.user.get("id")

            # Get Employment Request
            employment_request = await db.get(EmploymentRequest, employment_request_id)

            if not employment_request:
                logger.error(f"Employment Request with id {employment_request_id} was not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Employment Request not found"
                )

            # Get Employee
            employee = await db.get(User, auth_user_id)

            if not employee:
                logger.error(f"User with id {auth_user_id} was not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            is_employer = employment_request.employer_id == auth_user_id

            if employment_request.employee_id != auth_user_id and employment_request.employer_id != auth_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to perform this action"
                )

            if employment_update.status == EmploymentRequestsStatusEnum.ACCEPTED:
                role_id = await db.scalar(select(Role.id).where(Role.name == RoleEnum.EMPLOYEE))

                if not role_id:
                    logger.error(f"Role EMPLOYEE was not found")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Role not found"
                    )

                profession_name = await db.scalar(
                    select(Profession.name)
                    .where(Profession.id == employment_request.profession_id)
                )

                if not profession_name:
                    logger.error(f"Profession was not found")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Profession not found"
                    )

                employment_request.status = employment_update.status

                employee.employee_business_id = employment_request.business_id
                employee.profession = profession_name
                employee.role_id = role_id

                # Create Employees Schedules
                day_names = list(calendar.day_name)

                for idx, day in enumerate(day_names):
                    schedule = Schedule(
                            day_of_week=day,
                            day_week_index=idx,
                            user_id=auth_user_id,
                            business_id=employment_request.business_id,
                            start_time=None,
                            end_time=None
                        )
                    db.add(schedule)

                # Send Business Notification
                notification = Notification(
                        type=NotificationTypeEnum.EMPLOYMENT_REQUEST_ACCEPT,
                        sender_id=auth_user_id,
                        receiver_id=employment_request.employer_id,
                        data={"employment_request_id": employment_request.id},
                        message=f"Employment Accepted By {auth_user_id}"
                    )
                db.add(notification)

            else:
                # Delete Employment Request
                await db.execute(
                    delete(EmploymentRequest)
                    .where(EmploymentRequest.id == employment_request_id)
                )
                # Send Business Notification
                notification = Notification(
                        type=NotificationTypeEnum.EMPLOYMENT_REQUEST_DENIED,
                        sender_id=auth_user_id,
                        receiver_id=employment_request.employee_id if is_employer else employment_request.employer_id,
                        data={"employment_request_id": employment_request.id},
                        message=f"Employment Denied By {auth_user_id}"
                    )
                db.add(notification)

            previous_notification_result = await db.execute(
                select(Notification)
                .where(and_(
                    Notification.sender_id == employment_request.employer_id,
                    Notification.receiver_id == auth_user_id,
                    Notification.is_deleted == False
                ))
            )
            previous_notification = previous_notification_result.scalar_one_or_none()

            if not previous_notification:
                logger.error(f"Previous notification related to employment_request id {employment_request_id} was not found")
            previous_notification.is_deleted = True

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.error(f"Employment Respond failed. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')
