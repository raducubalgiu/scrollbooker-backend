from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func, UniqueConstraint, Index

from models import Base

class CommentPostLike(Base):
    __tablename__ = "comment_post_likes"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), index=True)
    post_author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("comment_id", "post_author_id", name="uq_comment_post_like"),
        Index("idx_comment_post_like_comment", "comment_id"),
        Index("idx_comment_post_like_author", "post_author_id"),
        Index("idx_comment_post_like_author_comment", "post_author_id", "comment_id")
    )