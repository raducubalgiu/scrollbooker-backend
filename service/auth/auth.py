import os

from pydantic import EmailStr
from starlette.requests import Request
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlalchemy import select, or_, desc
from starlette import status
from datetime import timedelta
from dotenv import load_dotenv
from core.enums.registration_step_enum import RegistrationStepEnum
from core.enums.role_enum import RoleEnum
from core.logger import logger
from core.crud_helpers import db_get_one
from core.security import hash_password, verify_password, create_token, decode_token
from core.dependencies import DBSession
from models import User, UserCounters, Role, Business, Permission
from schema.auth.auth import UserRegister, UserInfoResponse, UserInfoUpdate
from jose import JWTError

from schema.auth.token import RefreshToken, AuthResponse

load_dotenv()

async def register_user(db: DBSession, user_register: UserRegister):
    try:
        user = await db_get_one(db,
                                model=User,
                                filters={User.email: user_register.email},
                                raise_not_found=False)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User already registered')

        hashed = await hash_password(user_register.password)
        role = await db_get_one(db, model=Role, filters={Role.name: user_register.role_name})

        users_stmt = await db.execute(select(User.id).order_by(desc("id")))
        last_user = users_stmt.mappings().first()

        username = f"user{last_user.id}"
        fullname = f"user{last_user.id}"

        new_user = User(
            email=user_register.email,
            password=hashed,
            username=username,
            fullname=fullname,
            role_id=role.id,
            is_validated=False,
            registration_step=RegistrationStepEnum.COLLECT_USER_EMAIL_VALIDATION
        )
        db.add(new_user)
        await db.flush()

        # Create User Counters
        user_counters = UserCounters(user_id=new_user.id)
        db.add(user_counters)

        # # Send registration email
        # expires = timedelta(hours=24)
        # token = await create_token(
        #     data={"email": user_register.email},
        #     expires_at=expires,
        #     secret_key=os.getenv("SECRET_KEY")
        # )
        #
        # base_url = os.getenv("APP_BASE_URL")
        # link = f"{base_url}/verify-email/token={token}"
        #
        # await send_verification_email(to_email=str(user_register.email), verify_link=link)

        await db.commit()
        await db.refresh(new_user)

        return await generate_tokens(new_user.id, username, fullname, new_user.email, role.name)
    except Exception as e:
        await db.rollback()
        logger.error(f"User could not be registered. Error {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')

async def verify_user_email(db: DBSession, request: Request):
    auth_user_id = request.state.user.get("id")

    user = await db.get(User, auth_user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.registration_step = RegistrationStepEnum.COLLECT_USER_USERNAME
    db.add(user)

    await db.commit()

    return { "Detail": "Email verified" }

# async def verify_user_email(db: DBSession, token: str):
#     try:
#         email_data = await decode_token(token, os.getenv("SECRET_KEY"))
#
#         if not email_data or "email" not in email_data:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Token invalid or expired"
#             )
#
#         email = email_data.get("email")
#
#         user_stmt = await db.execute(select(User).where(and_(User.email == email)))
#         user = user_stmt.scalar_one_or_none()
#
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found"
#             )
#
#         user.registration_step = RegistrationStepEnum.COLLECT_USER_USERNAME
#         db.add(user)
#
#         await db.commit()
#
#         return {"Detail": "Email verified"}
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Something went wrong"
#         )

async def login_user(
        db: DBSession,
        username: str,
        password: str
) -> AuthResponse:
    user = await db_get_one(
        db = db,
        model=User,
        filters={User.username: username},
        joins=[joinedload(User.role)],
        raise_not_found=False
    )

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='This user is not registered yet')

    await verify_password(password, user.password)
    return await generate_tokens(user.id, username, user.fullname, user.email, user.role.name)

# Generate access and refresh tokens
async def generate_tokens(
        user_id: int,
        username: str,
        fullname: str,
        email: EmailStr,
        role: str
) -> AuthResponse:
    access_token = await create_token(
        data={
            "id": user_id,
            "sub": username,
            "fullname": fullname,
            "email": email,
            "role": role,
        },
        expires_at=timedelta(minutes=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))),
        secret_key=os.getenv("SECRET_KEY")
    )

    refresh_token = await create_token(
        data={
            "id": user_id,
            "sub": username,
            "fullname": fullname,
            "email": email,
            "role": role
        },
        expires_at=timedelta(days=float(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))),
        secret_key=os.getenv("REFRESH_SECRET_KEY")
    )
    return AuthResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer" )

async def get_refresh_token(
        db: DBSession,
        token: RefreshToken
) -> AuthResponse:
    try:
        payload = await decode_token(token.refresh_token, os.getenv("REFRESH_SECRET_KEY"))

        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        username = payload.get("sub")
        email = payload.get("email")

        user_stmt = await db.execute(
            select(User)
            .where(
                or_(
                    User.username == username,
                    User.email == email
                )
            )
            .options(joinedload(User.role))
        )

        user = user_stmt.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        logger.info(f"The Token was refreshed for user: {username}")
        return await generate_tokens(user.id, username, user.fullname, email, user.role.name)

    except JWTError as e:
        logger.error(f"Token could not be refreshed.Error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid refresh token')

async def get_user_info(db: DBSession, token: str) -> UserInfoResponse:
    try:
        payload = await decode_token(token, secret_key=os.getenv("SECRET_KEY"))

        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Invalid token')

        username = payload.get("sub")
        email = payload.get("email")

        user_stmt = await db.execute(
            select(User)
            .where(
                or_(
                    User.username == username,
                    User.email == email
                )
            )
            .options(
                joinedload(User.counters),
                joinedload(User.owner_business).load_only(Business.id, Business.business_type_id),
                joinedload(User.employee_business).load_only(Business.id, Business.business_type_id)
            )
        )

        user = user_stmt.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        business_id = (
            user.owner_business.id if user.owner_business
            else user.employee_business.id if user.employee_business
            else None
        )
        business_type_id = (
            user.owner_business.business_type_id if user.owner_business
            else user.employee_business.business_type_id if user.employee_business
            else None
        )

        return UserInfoResponse(
            id=user.id,
            username=user.username,
            fullname=user.fullname,
            business_id=business_id,
            business_type_id=business_type_id,
            is_validated=user.is_validated,
            registration_step=user.registration_step
        )

    except JWTError as e:
        logger.error(f"Invalid access token. Error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid access token')

async def get_user_permissions(db: DBSession, token: str):
    try:
        payload = await decode_token(token, secret_key=os.getenv("SECRET_KEY"))

        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Invalid token')

        username = payload.get("sub")
        email = payload.get("email")

        user_stmt = await db.execute(
            select(User)
            .where(
                or_(
                    User.username == username,
                    User.email == email
                )
            )
            .options(
                joinedload(User.role).joinedload(Role.permissions).load_only(Permission.name, Permission.code)
            )
        )

        user = user_stmt.unique().scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return user.role.permissions

    except JWTError as e:
        logger.error(f"Invalid access token. Error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid access token')

async def update_user_info(
        db: DBSession,
        user_update: UserInfoUpdate,
        token: str
) -> UserInfoResponse:
    try:
        payload = await decode_token(token, secret_key=os.getenv("SECRET_KEY"))

        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Invalid token')

        username = payload.get("sub")
        user = await db_get_one(db, model=User,
                                filters={User.username: username},
                                joins=[
                                    joinedload(User.counters),
                                    joinedload(User.owner_business).load_only(Business.id),
                                    joinedload(User.role).load_only(Role.name)
                                ])

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        if user.role.name == RoleEnum.EMPLOYEE:
            business_id = user.employee_business_id
        elif user.role.name == RoleEnum.BUSINESS:
            business_id = user.owner_business.id
        else:
            business_id = None

        user.username = user_update.username
        user.fullname = user_update.fullname
        user.bio = user_update.bio
        user.profession = user_update.profession

        await db.commit()
        await db.refresh(user)

        return UserInfoResponse(
            id=user.id,
            username=user.username,
            fullname=user.fullname,
            business_id=business_id,
            is_validated=user.is_validated
        )

    except JWTError as e:
        await db.rollback()
        logger.error(f"Invalid access token. Error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid access token')

