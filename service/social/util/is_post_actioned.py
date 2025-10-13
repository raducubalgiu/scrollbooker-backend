from typing import Type, Union

from sqlalchemy import select, and_
from core.dependencies import DBSession
from models import Like, BookmarkPost, Repost

ActionTable = Union[Type[Like], Type[BookmarkPost], Type[Repost]]

async def is_post_actioned(
    db: DBSession,
    table: ActionTable,
    post_id: int,
    auth_user_id: int
) -> bool:
    stmt = (
        select(1)
        .select_from(table)
        .where(
            and_(
                table.user_id == auth_user_id,
                table.post_id == post_id
            )
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar() is not None