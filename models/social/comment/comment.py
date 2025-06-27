from sqlalchemy.orm import relationship, backref

from models import Base
from sqlalchemy import Column, Integer, Index, ForeignKey, Text, TIMESTAMP, func

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)
    text = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")
    replies = relationship("Comment", backref=backref("parent", remote_side=[id]))

    __table_args__ = (
        Index("idx_comments_post", "post_id"),
        Index("idx_comments_user", "user_id"),
        Index("idx_comments_parent", "parent_id"),
        Index("idx_comments_post_user", "post_id", "user_id")
    )