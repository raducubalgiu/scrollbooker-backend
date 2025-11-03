from starlette.exceptions import HTTPException
from starlette import status
from starlette.requests import Request
from core.dependencies import DBSession
from core.enums.registration_step_enum import RegistrationStepEnum
from models import User
from schema.onboarding.onboarding import OnBoardingResponse
from schema.user.user import BirthDateUpdate, GenderUpdate
from service.onboarding.verify_registration_step import verify_registration_step
from service.user.user import update_user_birthdate, update_user_gender
from core.logger import logger

async def collect_client_birthdate(
    db: DBSession,
    birthdate_update: BirthDateUpdate,
    request: Request
) -> OnBoardingResponse:
    try:
        await verify_registration_step(
            db=db,
            request=request,
            registration_step=RegistrationStepEnum.COLLECT_CLIENT_BIRTHDATE
        )

        updated_birthdate = await update_user_birthdate(db, birthdate_update, request)

        if not updated_birthdate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Birthdate could not be updated"
            )

        user = await db.get(User, updated_birthdate.id)
        user.registration_step = RegistrationStepEnum.COLLECT_CLIENT_GENDER

        db.add(user)
        await db.commit()

        return OnBoardingResponse(
            is_validated=user.is_validated,
            registration_step=user.registration_step
        )

    except Exception as e:
        logger.error(f"Error on collecting client birthdate: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Something went wrong"
        )

async def collect_client_gender(
    db: DBSession,
    gender_update: GenderUpdate,
    request: Request
) -> OnBoardingResponse:
    try:
        await verify_registration_step(
            db=db,
            request=request,
            registration_step=RegistrationStepEnum.COLLECT_CLIENT_GENDER
        )

        updated_gender = await update_user_gender(db, gender_update, request)

        if not updated_gender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gender could not be updated"
            )

        user = await db.get(User, updated_gender.id)
        user.registration_step = RegistrationStepEnum.COLLECT_CLIENT_LOCATION_PERMISSION

        db.add(user)
        await db.commit()

        return OnBoardingResponse(
            is_validated=user.is_validated,
            registration_step=user.registration_step
        )

    except Exception as e:
        logger.error(f"Error on collecting client gender: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Something went wrong"
        )