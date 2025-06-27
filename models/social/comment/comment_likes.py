from models import Base
from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP, func, UniqueConstraint, Index

class CommentLike(Base):
    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", name="uq_comment_like"),
        Index("idx_commentlike_comment", "comment_id"),
        Index("idx_commentlike_user", "user_id"),
        Index("idx_commentlike_user_comment", "user_id", "comment_id")
    )
