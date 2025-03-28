from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Boolean, Index
from sqlalchemy.orm import relationship

from app.models import Base
from app.models.booking.nomenclature.business_type_filters import business_type_filters

class Filter(Base):
    __tablename__ = "filters"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    active = Column(Boolean, nullable=False, default=True, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    business_types = relationship("BusinessType", secondary=business_type_filters, back_populates="filters")
    sub_filters = relationship("SubFilter", back_populates="filter")

    __table_args__ = (
        Index("idx_filter_name", "name"),
        Index("idx_filter_active", "active"),
        Index("idx_filter_name_active", "name", "active")
    )