from fastapi import HTTPException
from starlette.requests import Request
from starlette import status
from app.core.enums.enums import RoleEnum
from app.core.crud_helpers import db_create, db_get_one
from app.core.dependencies import DBSession
from app.models import EmploymentRequest, Business, User, Role
from app.schema.booking.employment_request import EmploymentRequestCreate, EmploymentRequestUpdate
from app.core.logger import logger

async def send_employment_request(db: DBSession, new_employment: EmploymentRequestCreate,  request: Request):
    auth_user_id = request.state.user.get("id")
    business = await db_get_one(db, model=Business, filters={Business.owner_id: auth_user_id}, raise_not_found=False)

    if not business:
        logger.logger(f"Business with ID: {auth_user_id} doesn't have the Business defined")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='You do not have permission to perform this action')

    return await db_create(db, model=EmploymentRequest, create_data=new_employment,
                    extra_params={'employer_id': auth_user_id, 'business_id': business.id})

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
