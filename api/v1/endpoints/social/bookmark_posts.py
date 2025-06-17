from fastapi import APIRouter
from starlette.requests import Request
from starlette import status
from backend.core.dependencies import DBSession
from backend.service.social.bookmark_posts import bookmark_post_by_id, unbookmark_post_by_id

router = APIRouter(tags=["Bookmark Posts"])

@router.post("/posts/{post_id}/bookmark-posts",
             summary='Bookmark Post By Post Id',
             status_code=status.HTTP_201_CREATED)
async def bookmark_post(db: DBSession, post_id: int, request: Request):
    return await bookmark_post_by_id(db, post_id, request)

@router.delete("/posts/{post_id}/bookmark-postss",
            summary='Unbookmark Post by Post Id',
            status_code=status.HTTP_204_NO_CONTENT)
async def unbookmark_post(db: DBSession, post_id: int, request: Request):
    return await unbookmark_post_by_id(db, post_id, request)