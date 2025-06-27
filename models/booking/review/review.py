from sqlalchemy.orm import relationship, backref

from models import Base
from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP, func, Index

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    review = Column(String(500), nullable=False, index=True)
    rating = Column(Integer, nullable=False, index=True)
    like_count = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Foreign keys
    parent_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    service_id = Column(Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)

    customer = relationship("User", foreign_keys=[customer_id], back_populates="customer_reviews")
    business_or_employee = relationship("User", foreign_keys=[user_id],
                                        back_populates="business_or_employee_reviews")

    service = relationship("Service", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    replies = relationship("Review", backref=backref("parent", remote_side=[id]))

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_user_rating", "user_id", "rating"),

        Index("idx_service_id", "service_id"),
        Index("idx_product_id", "product_id"),
        Index("idx_customer_id", "customer_id"),
    )
