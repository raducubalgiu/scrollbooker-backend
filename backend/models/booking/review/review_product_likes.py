from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func, UniqueConstraint, Index
from backend.models import Base

class ReviewProductLike(Base):
    __tablename__ = "review_product_likes"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), index=True)
    # Business or Employee
    product_author_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # __table_args__ = (
    #     UniqueConstraint("review_id", "product_author_user_id", name="uq_review_product_like"),
    #     Index("idx_reviewproductlikes_review", "review_id"),
    #     Index("idx_reviewproductlikes_author", "product_author_user_id"),
    #     Index("idx_reviewproductlikes_author_review", "product_author_user_id", "review_id")
    # )