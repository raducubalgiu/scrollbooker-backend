from models import Base
from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP, func, UniqueConstraint, Index

class ReviewLike(Base):
    __tablename__ = "review_likes"

    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="uq_review_like"),
        Index("idx_review_likes_review", "review_id"),
        Index("idx_review_likes_user", "user_id"),
        Index("idx_review_likes_user_review", "user_id", "review_id")
    )