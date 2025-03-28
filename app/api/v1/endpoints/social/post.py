from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from app.core.dependencies import DBSession
from app.core.enums.enums import PostAction
from app.schema.social.post import PostResponse, PostCreate
from app.schema.social.comment import CommentCreate, CommentBase
from app.service.social.post import create_new_post, get_post_likes_by_post_id
from app.service.social.post_action import check_post_action, perform_post_action, remove_post_action
from app.service.social.comment import create_new_comment, like_post_comment, unlike_post_comment, get_comments_by_post_id

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", response_model=PostResponse)
async def create_post(db: DBSession, new_post: PostCreate, request: Request):
    return await create_new_post(db, new_post, request)

@router.get("/{post_id}/likes")
async def get_post_likes(db: DBSession, post_id: int, page: int, limit: int, request: Request):
    return await get_post_likes_by_post_id(db, post_id, page, limit, request)

# LIKES
@router.get("/{post_id}/likes/check", response_model=bool)
async def check_like(db: DBSession, post_id: int, request: Request):
    return await check_post_action(db, post_id, request, action=PostAction.LIKE)

@router.post("/{post_id}/likes", status_code=status.HTTP_201_CREATED)
async def like(db: DBSession, post_id: int, request: Request):
    return await perform_post_action(db, post_id, request, action=PostAction.LIKE)

@router.delete("/{post_id}/likes", status_code=status.HTTP_204_NO_CONTENT)
async def unlike(db: DBSession, post_id: int, request: Request):
    return await remove_post_action(db, post_id, request, action=PostAction.LIKE)

# SAVES
@router.get("/{post_id}/saves/check", response_model=bool)
async def check_save(db: DBSession, post_id: int, request: Request):
    return await check_post_action(db, post_id, request, action=PostAction.SAVE)

@router.post("/{post_id}/saves", status_code=status.HTTP_201_CREATED)
async def save(db: DBSession, post_id: int, request: Request):
    return await perform_post_action(db, post_id, request, action=PostAction.SAVE)

@router.delete("/{post_id}/saves", status_code=status.HTTP_204_NO_CONTENT)
async def unsave(db: DBSession, post_id: int, request: Request):
    return await remove_post_action(db, post_id, request, action=PostAction.SAVE)

# SHARES
@router.get("/{post_id}/shares/check", response_model=bool)
async def check_share(db: DBSession, post_id: int, request: Request):
    return await check_post_action(db, post_id, request, action=PostAction.SHARE)

@router.post("/{post_id}/shares", status_code=status.HTTP_201_CREATED)
async def share(db: DBSession, post_id: int, request: Request):
    return await perform_post_action(db, post_id, request, action=PostAction.SHARE)

@router.delete("/{post_id}/shares", status_code=status.HTTP_204_NO_CONTENT)
async def unshare(db: DBSession, post_id: int, request: Request):
    return await remove_post_action(db, post_id, request, action=PostAction.SHARE)

# COMMENTS
@router.get("/{post_id}/comments")
async def get_comments(db: DBSession, post_id: int, page: int, limit: int, request: Request):
    return await get_comments_by_post_id(db, post_id, page, limit, request)

@router.post("/{post_id}/comments", response_model=CommentBase)
async def create_comment(db: DBSession, post_id: int, comment_data: CommentCreate, request: Request):
    return await create_new_comment(db, post_id, comment_data, request)

@router.post("/{post_id}/comments/{comment_id}/like", status_code=status.HTTP_201_CREATED)
async def like_comment(db: DBSession, post_id: int, comment_id: int, request: Request):
    return await like_post_comment(db, post_id, comment_id, request)

@router.delete("/{post_id}/comments/{comment_id}/unlike", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_comment(db: DBSession, post_id: int, comment_id: int, request: Request):
    return await unlike_post_comment(db, post_id, comment_id, request)
