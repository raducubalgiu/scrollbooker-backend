from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from dotenv import load_dotenv
from core.security import oauth2_bearer
from schema.auth.auth import UserRegister, UserRegisterResponse, UserInfoResponse, UserInfoUpdate
from schema.auth.token import Token, RefreshToken
from service.auth.auth import login_user, register_user, get_refresh_token, get_user_info, update_user_info, \
    get_user_permissions
from core.dependencies import DBSession
from models import User
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["Auth"])

load_dotenv()

@router.get("/")
async def get_users(db: DBSession):
    users = await db.execute(select(User))
    return users.scalars().all()

@router.post("/register",
             summary='Register New User',
             status_code=status.HTTP_201_CREATED)
async def register(db: DBSession, user_register: UserRegister):
    return await register_user(db, user_register)

@router.post("/login", response_model=Token)
async def login(db: DBSession, form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_user(db, form_data.username, form_data.password)

@router.post("/refresh")
async def refresh_token(db: DBSession, token: RefreshToken):
    return await get_refresh_token(db, token)

@router.get("/user-info", response_model=UserInfoResponse)
async def user_info(db: DBSession, token: str = Depends(oauth2_bearer)):
    return await get_user_info(db, token)

@router.get("/user-permissions")
async def user_permissions(db: DBSession, token: str = Depends(oauth2_bearer)):
    return await get_user_permissions(db, token)

@router.put("/update-user-info", response_model=UserInfoResponse)
async def user_info(db: DBSession, user_update: UserInfoUpdate, token: str = Depends(oauth2_bearer)):
    return await update_user_info(db, user_update, token)
