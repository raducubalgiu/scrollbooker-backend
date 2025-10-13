from enum import Enum
from typing import Type, Union, Final

from sqlalchemy import update, func
from sqlalchemy.orm import InstrumentedAttribute

from core.dependencies import DBSession
from models import Like, BookmarkPost, Repost, Post

ActionTable = Union[Type[Like], Type[BookmarkPost], Type[Repost]]

class PostActionEnum(Enum):
    ADD = 1
    REMOVE = -1

COUNTER_COLUMN_MAP: Final[dict[type, InstrumentedAttribute]] = {
    Like: Post.like_count,
    Repost: Post.repost_count,
    BookmarkPost: Post.bookmark_count
}

async def update_post_counter(
    db: DBSession,
    model: ActionTable,
    post_id: int,
    action: PostActionEnum,
) -> None:
    column = COUNTER_COLUMN_MAP[model]

    delta = action.value

    stmt = (
        update(Post)
        .where(Post.id == post_id)
        .values({ column: func.greatest(column + delta, 0) })
    )
    await db.execute(stmt)