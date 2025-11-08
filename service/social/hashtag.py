from fastapi import HTTPException

from core.crud_helpers import db_get_one, db_create
from core.dependencies import DBSession
from starlette import status
from schema.social.hashtag import HashtagCreate
from models import Hashtag

async def create_new_hashtag(db: DBSession, new_hashtag: HashtagCreate):
    hashtag = await db_get_one(db, model=Hashtag, filters={ Hashtag.name: new_hashtag.name }, raise_not_found=False)

    if hashtag:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Hashtag already present!')

    return await db_create(db, model=Hashtag, create_data=new_hashtag)