from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func, UniqueConstraint, Index
from models import Base

class ReviewProductOwnerLike(Base):
    __tablename__ = "review_product_owner_likes"

    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"))
    product_owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("review_id", "product_owner_id", name="uq_review_product_owner_like"),
        Index("idx_review_product_owner_likes_review", "review_id"),
        Index("idx_review_product_owner_likes_product_owner", "product_owner_id"),
        Index("idx_review_product_owner_likes_product_owner_review", "product_owner_id", "review_id")
    )