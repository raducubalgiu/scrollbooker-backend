from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from core.database import Base

class BookmarkPost(Base):
    __tablename__ = "bookmark_posts"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bookmark_posts")
    post = relationship("Post", back_populates="bookmark_posts")

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="unique_user_post_bookmark"),
        Index("idx_bookmark_posts_user_id", "user_id"),
        Index("idx_bookmark_posts_post_id", "post_id"),
        Index("idx_bookmarks_use_posts_post", "user_id", "post_id")
    )