from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv
import os
from jose import jwt, JWTError # type: ignore
from passlib.context import CryptContext # type: ignore
from fastapi.concurrency import run_in_threadpool
from fastapi.security import OAuth2PasswordBearer
from core.logger import logger

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

# Hash Password
async def hash_password(password: str) -> str:
    return await run_in_threadpool(pwd_context.hash, password)

# Verify password
async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return await run_in_threadpool(pwd_context.verify, plain_password, hashed_password)

# Create JWT Token
async def create_token(data:dict, expires_at: timedelta, secret_key: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_at
    to_encode.update({"exp": expire})
    return await run_in_threadpool(jwt.encode, to_encode, secret_key, algorithm=os.getenv("ALGORITHM"))

# Decode JWT token
async def decode_token(token: str, secret_key: str) -> Optional[dict]:
    try:
        return await run_in_threadpool(jwt.decode, token, secret_key, algorithms=[os.getenv("ALGORITHM")])
    except JWTError as e:
        logger.error(f"Token could not be decoded. Error: {e}")
        return None