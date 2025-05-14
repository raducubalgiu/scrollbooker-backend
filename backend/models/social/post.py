from sqlalchemy.orm import relationship
from backend.models import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey, Boolean, ARRAY, Text, BigInteger, Index

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False)
    bookable = Column(Boolean, nullable=False, default=False, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)

    hashtags = Column(ARRAY(Text), nullable=True)
    mentions = Column(ARRAY(BigInteger), nullable=True)

    like_count = Column(Integer, nullable=False, default=0)
    share_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    save_count = Column(Integer, nullable=False, default=0)

    expiration_time = Column(TIMESTAMP(timezone=True), nullable=True, default=None, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relations
    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete")
    media_files = relationship("PostMedia", back_populates="post", cascade="all, delete")

    __table_args__ = (
        Index("idx_post_user", "user_id"),
        Index("idx_post_created_at", "created_at")
    )