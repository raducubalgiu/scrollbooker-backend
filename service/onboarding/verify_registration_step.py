from typing import Optional
from fastapi import HTTPException, status

from sqlalchemy import select
from core.dependencies import DBSession, AuthenticatedUser
from core.enums.registration_step_enum import RegistrationStepEnum
from models import User
from core.logger import logger

async def verify_registration_step(
    db: DBSession,
    auth_user: AuthenticatedUser,
    registration_step: RegistrationStepEnum
) -> None:
    auth_user_id: int = auth_user.id

    current_step: Optional[RegistrationStepEnum] = await db.scalar(
        select(User.registration_step)
        .where(User.id == auth_user_id)
    )

    if current_step is None:
        logger.error(f"ERROR: User with id {auth_user_id} not found in verify_registration_step")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if current_step != registration_step:
        logger.error(
            f"ERROR: User with id: {auth_user_id} is trying to update his username in step: {auth_user.registration_step}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You do not have permissions to perform this action'
        )