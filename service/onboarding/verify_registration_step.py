from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette import status
from sqlalchemy import select
from core.dependencies import DBSession
from core.enums.registration_step_enum import RegistrationStepEnum
from models import User
from core.logger import logger

async def verify_registration_step(db: DBSession, request: Request, registration_step: RegistrationStepEnum):
    auth_user_id = request.state.user.get("id")

    auth_user_stmt = await db.execute(
        select(User.registration_step)
        .where(User.id == auth_user_id)
    )
    auth_user = auth_user_stmt.mappings().first()

    if auth_user.registration_step is not registration_step:
        logger.error(
            f"ERROR: User with id: {auth_user_id} is trying to update his username in step: {auth_user.registration_step}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You do not have permissions to perform this action'
        )