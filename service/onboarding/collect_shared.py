from sqlalchemy import select
from sqlalchemy.orm import joinedload
from starlette.exceptions import HTTPException
from starlette import status
from starlette.requests import Request
from core.logger import logger
from core.dependencies import DBSession
from core.enums.registration_step_enum import RegistrationStepEnum
from core.enums.role_enum import RoleEnum
from models import User
from schema.onboarding.onboarding import OnBoardingResponse
from schema.user.user import UsernameUpdate
from service.onboarding.verify_registration_step import verify_registration_step
from service.user.user import update_user_username

async def collect_user_username(db: DBSession, username_update: UsernameUpdate, request: Request):
    try:
        await verify_registration_step(
            db=db,
            request=request,
            registration_step=RegistrationStepEnum.COLLECT_USER_USERNAME
        )

        updated_username = await update_user_username(db, username_update, request)

        if not updated_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username could not be updated'
            )

        user_stmt = await db.execute(
            select(User)
            .where(User.id == updated_username.id)
            .options(joinedload(User.role))
        )
        user = user_stmt.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User not found'
            )

        if user.role.name is RoleEnum.BUSINESS:
            user.registration_step = RegistrationStepEnum.COLLECT_BUSINESS
        else:
            user.registration_step = RegistrationStepEnum.COLLECT_CLIENT_BIRTHDATE

        db.add(user)
        await db.commit()

        return OnBoardingResponse(
            is_validated=user.is_validated,
            registration_step=user.registration_step
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Something went wrong when collecting username. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User not found'
        )

async def collect_user_location_permission(db: DBSession, request: Request):
    auth_user_id = request.state.user.get("id")

    user = await db.get(User, auth_user_id)

    user.is_validated = True
    user.registration_step = None

    db.add(user)
    await db.commit()

    return OnBoardingResponse(
        is_validated=user.is_validated,
        registration_step=user.registration_step
    )
