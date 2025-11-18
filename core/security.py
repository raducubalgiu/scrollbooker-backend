from datetime import datetime, timedelta, timezone
from typing import Optional, cast, Any

from argon2.exceptions import InvalidHash
from dotenv import load_dotenv
import os

from fastapi import HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.concurrency import run_in_threadpool
from fastapi.security import OAuth2PasswordBearer
from passlib.exc import UnknownHashError
from pydantic.v1 import EmailStr
from starlette import status

from core.logger import logger
from schema.auth.token import TokenPayload, EncodedTokenClaims

load_dotenv()

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

# Hash Password
async def hash_password(password: str) -> str:
    return cast(
        str,
        await run_in_threadpool(pwd_context.hash, password)
    )

async def verify_password(plain_password: str, hashed_password: str) -> None:
    try:
        ok = await run_in_threadpool(pwd_context.verify, plain_password, hashed_password)
    except (UnknownHashError, InvalidHash, ValueError, TypeError) as e:
        logger.error(f"Password verify failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    except Exception as e:
        logger.exception(f"Password verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not verify credentials",
        )

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

# Create JWT Token
async def create_token(
        payload: TokenPayload,
        expires_at: timedelta,
        secret_key: str
) -> str:
    expire = datetime.now(timezone.utc) + expires_at

    claims: EncodedTokenClaims = {
        "id": payload.id,
        "sub": payload.username,
        "fullname": payload.fullname,
        "email": str(payload.email),
        "role": payload.role,
        "exp": expire
    }

    mutable_claims: dict[str, Any] = dict(claims)
    algorithm = os.getenv("ALGORITHM") or "HS256"

    return cast(
        str,
        await run_in_threadpool(jwt.encode, mutable_claims, secret_key, algorithm=algorithm)
    )

# Decode JWT token
async def decode_token(token: str, secret_key: str) -> Optional[TokenPayload]:
    try:
        algorithm = os.getenv("ALGORITHM") or "HS256"

        raw = await run_in_threadpool(jwt.decode, token, secret_key, algorithms=[algorithm])

        claims = cast(EncodedTokenClaims, raw)

        return TokenPayload(
            id=claims["id"],
            username=claims["sub"],
            fullname=claims["fullname"],
            email=EmailStr(claims["email"]),
            role=claims["role"]
        )

    except JWTError as e:
        logger.error(f"Token could not be decoded. Error: {e}")
        return None