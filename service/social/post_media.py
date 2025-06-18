from collections import defaultdict
from typing import List, Dict

from backend.core.dependencies import DBSession
from backend.models import PostMedia
from sqlalchemy import select

from backend.schema.social.post_media import PostMediaResponse

async def get_post_media(
        db: DBSession, post_ids: List[int]
) -> Dict[int, List[PostMediaResponse]]:
    stmt = (
        select(PostMedia)
        .where(PostMedia.post_id.in_(post_ids))
        .order_by(PostMedia.post_id, PostMedia.order_index)
    )

    result = await db.execute(stmt)
    rows = result.scalars().all()

    media_map = defaultdict(list)

    for media in rows:
        media_map[media.post_id].append(PostMediaResponse.model_validate(media))

    return media_map