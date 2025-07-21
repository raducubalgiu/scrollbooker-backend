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
from service.user.user import update_user_username

async def collect_user_username(db: DBSession, username_update: UsernameUpdate, request: Request):
    auth_user_id = request.state.user.get("id")

    auth_user_stmt = await db.execute(
        select(User.registration_step)
        .where(User.id == auth_user_id)
    )
    auth_user = auth_user_stmt.mappings().first()

    if auth_user.registration_step is not RegistrationStepEnum.COLLECT_USER_USERNAME:
        logger.error(f"ERROR: User with id: {auth_user_id} is trying to update his username in step: {auth_user.registration_step}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You do not have permissions to perform this action'
        )

    try:
        updated_username = await update_user_username(db, username_update, request)

        if not updated_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username could not be updated'
            )

        updated_user_stmt = await db.execute(
            select(User)
            .where(User.username == updated_username.username)
            .options(joinedload(User.role))
        )
        updated_user = updated_user_stmt.scalar_one_or_none()

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User not found'
            )

        if updated_user.role.name is RoleEnum.BUSINESS:
            updated_user.registration_step = RegistrationStepEnum.COLLECT_BUSINESS
        else:
            updated_user.registration_step = RegistrationStepEnum.COLLECT_CLIENT_BIRTHDATE

        db.add(updated_user)
        await db.commit()

        return OnBoardingResponse(
            is_validated=updated_user.is_validated,
            registration_step=updated_user.registration_step
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Something went wrong when collecting username. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User not found'
        )