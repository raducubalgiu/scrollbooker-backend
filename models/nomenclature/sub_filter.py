from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, ForeignKey, Index
from sqlalchemy.orm import relationship

from models import Base
from models.booking.product_sub_filters import product_sub_filters

class SubFilter(Base):
    __tablename__ = "sub_filters"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    active = Column(Boolean, nullable=False, default=True, index=True)
    filter_id = Column(Integer, ForeignKey("filters.id", ondelete="CASCADE"), nullable=False, index=True)

    filter = relationship("Filter", back_populates="sub_filters")
    products = relationship("Product", secondary=product_sub_filters, back_populates="sub_filters")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_sub_filter_name", "name"),
        Index("idx_sub_filter_active", "active"),
        Index("idx_sub_filter_filter_id", "filter_id"),
        Index("idx_sub_filter_name_filter_id", "name", "filter_id"),
        Index("idx_sub_filter_name_active_filter_id", "name", "active", "filter_id")
    )