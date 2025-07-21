from fastapi import APIRouter
from starlette.requests import Request

from core.dependencies import DBSession
from schema.user.user import UsernameUpdate
from service.onboarding.collect_user_username import collect_user_username

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

@router.patch("/collect-user-username",
              summary='Collect User Username')
async def collect_username(db: DBSession, username_update: UsernameUpdate, request: Request):
    return await collect_user_username(db, username_update, request)