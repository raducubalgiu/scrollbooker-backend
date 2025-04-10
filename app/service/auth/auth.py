import os
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from starlette import status
from datetime import timedelta
from sqlalchemy import select
from dotenv import load_dotenv

from app.core.enums.enums import RoleEnum
from app.core.logger import logger
from app.core.crud_helpers import db_get_one
from app.core.security import hash_password, verify_password, create_token, decode_token
from app.core.dependencies import DBSession
from app.models import User, UserCounters, Role, Business
from app.schema.auth.auth import UserRegister, UserInfoResponse
from jose import JWTError #type: ignore

load_dotenv()

async def register_user(db: DBSession, user_register: UserRegister):
    user = await db_get_one(db, model=User, filters={User.email: user_register.email}, raise_not_found=False)

    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already registered')

    # Hash the password async
    hashed = await hash_password(user_register.password)

    # This will be removed in the future
    get_role = await db_get_one(db, model=Role, filters={Role.name: user_register.role_name})

    try:
        new_user = User(
            email=user_register.email,
            password=hashed,
            username=user_register.username,
            role_id=get_role.id
        )
        db.add(new_user)
        await db.flush()
        user_counters = UserCounters(user_id=new_user.id)
        db.add(user_counters)

        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        logger.error(f"User could not be registered. Error {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')


async def login_user(db: DBSession, username: str, password: str):
    user = await db_get_one(db, model=User, filters={User.username: username}, joins=[joinedload(User.role)])

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='This user is not registered yet')

    password = await verify_password(password, user.password)

    if not password:
        raise HTTPException(status_code=400, detail="Password doesn't match")

    return await generate_tokens(username, user.id, user.role.name)

# Generate access and refresh tokens
async def generate_tokens(username: str, user_id: int, role: str):
    access_token = await create_token(
        data={"sub": username, "id": user_id, "role": role},
        expires_at=timedelta(minutes=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))),
        secret_key=os.getenv("SECRET_KEY")
    )

    refresh_token = await create_token(
        data={"sub": username, "id": user_id, "role": role},
        expires_at=timedelta(days=float(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))),
        secret_key=os.getenv("REFRESH_SECRET_KEY")
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

async def get_refresh_token(db: DBSession, token: str):
    try:
        payload = await decode_token(token, os.getenv("SECRET_KEY"))

        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        username = payload.get("sub")
        stmt = await db.execute(
            select(User).filter(User.username == username))  # type: ignore
        user = stmt.scalars().first()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        access_token_expires = timedelta(minutes=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))

        access_token = await create_token(
            data={"sub": username},
            expires_at=access_token_expires,
            secret_key=os.getenv("SECRET_KEY")
        )

        return {"access_token": access_token, "refresh_token": token, "token_type": "bearer"}
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid refresh token')

async def get_user_info(db: DBSession, token: str):
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

        return {
            "id": user.id,
            "fullname": user.fullname,
            "avatar": user.avatar,
            "username": user.username,
            "business_id": business_id,
            "email": user.email,
            "counters": user.counters,
            "profession": user.profession
        }

    except JWTError as e:
        logger.error(f"Invalid access token. Error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid access token')
