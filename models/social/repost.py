from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func, UniqueConstraint, Index, String
from sqlalchemy.orm import relationship

from core.database import Base

class Repost(Base):
    __tablename__ = "reposts"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    original_poster_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    comment = Column(String(300), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id], back_populates="reposts")
    original_poster = relationship("User", foreign_keys=[original_poster_id], back_populates="reposts")
    post = relationship("Post", back_populates="reposts")

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="unique_user_post_reposts"),
        Index("idx_reposts_posts_user_id", "user_id"),
        Index("idx_reposts_posts_post_id", "post_id"),
        Index("idx_reposts_use_posts_post", "user_id", "post_id")
    )