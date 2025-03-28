from fastapi import HTTPException
from starlette import status
from starlette.requests import Request
from sqlalchemy import select, insert, update, delete
from app.core.dependencies import DBSession
from app.core.enums.enums import PostAction
from app.models import post_shares, post_likes, post_saves, Post
from app.core.logger import logger

ACTION_TABLES = {
    PostAction.LIKE: post_likes,
    PostAction.SAVE: post_saves,
    PostAction.SHARE: post_shares
}

async def check_post_action(db: DBSession, post_id: int, request: Request, action: PostAction):
    auth_user_id = request.state.user.get("id")
    table = ACTION_TABLES[action]

    stmt = await db.execute(select(table)
               .where((table.c.post_id == post_id) & (table.c.user_id == auth_user_id))) #type: ignore
    post = stmt.scalar_one_or_none()

    return True if post else False

async def perform_post_action(db: DBSession, post_id: int, request: Request, action: PostAction):
    auth_user_id = request.state.user.get("id")
    table = ACTION_TABLES[action]
    action_split = action.split(".")[0].lower()

    is_action = await check_post_action(db, post_id, request, action)

    if is_action:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Already {action_split}d this post")
    try:
        await db.execute(insert(table).values(post_id=post_id, user_id=auth_user_id))

        counter_column = f"{action.lower()}_count"

        await db.execute(
            update(Post)
            .where(Post.id == post_id) # type: ignore
            .values({counter_column: getattr(Post, counter_column) + 1})
        )

        await db.commit()
        return {"detail": f"User {auth_user_id} {action_split}d post {post_id}"}

    except Exception as e:
        await db.rollback()
        logger.error(f"Post Action: {action} could not be performed. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Something went wrong")

async def remove_post_action(db: DBSession, post_id: int, request: Request, action: PostAction):
    auth_user_id = request.state.user.get("id")
    table = ACTION_TABLES[action]
    action_split = action.split(".")[0].lower()

    is_action = await check_post_action(db, post_id, request, action)

    if is_action is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You didn't {action_split} like this post")
    try:
        await db.execute(delete(table).where(
            (table.c.post_id == post_id) & (table.c.user_id == auth_user_id) # type: ignore
        ))

        counter_column = f"{action.lower()}_count"

        await db.execute(
            update(Post)
            .where(Post.id == post_id)  # type: ignore
            .values({counter_column: getattr(Post, counter_column) - 1})
        )

        await db.commit()

    except Exception as e:
        await db.rollback()
        logger.error(f"Post Action: {action} could not be performed. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Something went wrong')