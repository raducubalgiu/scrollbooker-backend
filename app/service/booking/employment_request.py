from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from starlette.requests import Request
from sqlalchemy import select, or_
from starlette import status
from app.core.enums.enums import RoleEnum
from app.core.crud_helpers import db_create, db_get_one, db_delete, db_get_all
from app.core.dependencies import DBSession
from app.models import EmploymentRequest, Business, User, Role, Notification, Profession
from app.schema.booking.employment_request import EmploymentRequestCreate, EmploymentRequestUpdate
from app.core.logger import logger

async def get_employment_requests_by_user_id(db: DBSession, user_id: int, request: Request):
    auth_user_id = request.state.user.get("id")
    user = await db_get_one(db, model=User, filters={User.id: user_id}, joins=[joinedload(User.role)])

    if user.id != auth_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You do not have permission to perform this action')

    field_name = "employer_id" if user.role.name == RoleEnum.BUSINESS else "employee_id"

    employment_requests = await db_get_all(db,
                                           model=EmploymentRequest,
                                           filters={getattr(EmploymentRequest, field_name): user_id, EmploymentRequest.status: 'pending'},
                                           joins=[
                                               joinedload(EmploymentRequest.employer).load_only(User.id, User.username, User.fullname, User.avatar),
                                               joinedload(EmploymentRequest.employee).load_only(User.id, User.username, User.fullname, User.avatar),
                                               joinedload(EmploymentRequest.profession).load_only(Profession.id, Profession.name)
                                           ])
    return employment_requests

async def send_employment_request(db: DBSession, employment_create: EmploymentRequestCreate,  request: Request):
    auth_user_id = request.state.user.get("id")
    business = await db_get_one(db, model=Business, filters={Business.owner_id: auth_user_id}, raise_not_found=False)
    profession = await db_get_one(db, model=Profession, filters={Profession.id: employment_create.profession_id})

    if not business:
        logger.logger(f"Business with ID: {auth_user_id} doesn't have the Business defined")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='You do not have permission to perform this action')
    try :
        employment_request = await db_create(db, model=EmploymentRequest, create_data=employment_create,
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

async def delete_employment_request_by_id(db: DBSession, employment_request_id: int, request: Request):
    auth_user_id = request.state.user.get("id")
    user = await db_get_one(db, model=User, filters={User.id: auth_user_id}, joins=[joinedload(User.role)])
    employment_request = await db.get(EmploymentRequest, employment_request_id)

    is_employee_or_business = await db.execute(
        select(EmploymentRequest)
        .where(
            EmploymentRequest.id == employment_request_id, #type: ignore
            or_(
                employment_request.employer_id == auth_user_id,
                employment_request.employee_id == auth_user_id
            )
        )
    )

    if not is_employee_or_business.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You do not have permission to perform this action')

    try:
        await db_delete(db, model=EmploymentRequest, resource_id=employment_request_id)

        if user.role.name == RoleEnum.BUSINESS:
            notification = Notification(
                type="employment_request_delete",
                sender_id=auth_user_id,
                receiver_id=employment_request.employee_id,
                data={ "employment_request_id": employment_request.id },
                message="Employment Deleted By Business"
            )
            db.add(notification)

        if user.role.name == RoleEnum.CLIENT:
            notification = Notification(
                type="employment_request_delete",
                sender_id=auth_user_id,
                receiver_id=employment_request.employer_id,
                data={ "employment_request_id": employment_request.id },
                message="Employment Deleted By Business"
            )
            db.add(notification)

        await db.commit()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Something went wrong')

async def accept_employment_request(db: DBSession,
                                    employment_request_id: int,
                                    employment_update: EmploymentRequestUpdate,
                                    request: Request):

    auth_user_id = request.state.user.get("id")
    employment_request = await db.get(EmploymentRequest, employment_request_id)

    try:
        if employment_update.status == 'accepted':
            employment_request.status = employment_update.status

            employee = await db.get(User, auth_user_id)
            employee.employee_business_id = employment_request.business_id

            employee_role = await db_get_one(db, model=Role, filters={Role.name: RoleEnum.EMPLOYEE})
            employee.role_id = employee_role.id

            business = await db.get(Business, employment_request.business_id)
            if not business.has_employees:
                business.has_employees = True

            await db.commit()
            return {"detail": "Employment request Accepted"}
        else:
            await db.delete(employment_request)
            await db.commit()
            return {"detail": "Employment Request Denied"}

    except Exception as e:
        logger.error(f"Accept employment failed. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')
