from sqlalchemy import Table, Column, Integer, ForeignKey, Index, TIMESTAMP, func
from app.models import Base

post_saves = Table(
    "post_saves",
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id', ondelete="CASCADE"), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.now()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()),

    Index("idx_post_saves_post_id", "post_id"),
    Index("idx_post_saves_user_id", "user_id"),
    Index("idx_post_saves_post_user", "post_id", "user_id")
)