from fastapi import APIRouter

from backend.core.dependencies import DBSession, SuperAdminSession
from backend.schema.social.hashtag import HashtagResponse, HashtagCreate
from backend.service.social.hashtag import create_new_hashtag

router = APIRouter(prefix="/hashtags", tags=["Hashtags"])

@router.post("/", response_model=HashtagResponse, dependencies=[SuperAdminSession])
async def create_hashtag(db: DBSession, new_hashtag: HashtagCreate):
    return await create_new_hashtag(db, new_hashtag)

