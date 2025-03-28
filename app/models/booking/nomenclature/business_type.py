from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, Index, ForeignKey
from sqlalchemy.orm import relationship
from app.models import Base
from app.models.booking.nomenclature.business_type_filters import business_type_filters
from app.models.booking.nomenclature.business_type_professions import business_type_professions
from app.models.booking.nomenclature.service_business_types import service_business_types

class BusinessType(Base):
    __tablename__ = "business_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    active = Column(Boolean, nullable=False, default=True)
    business_domain_id = Column(Integer, ForeignKey("business_domains.id", ondelete="CASCADE"), nullable=False)

    services = relationship("Service", secondary=service_business_types, back_populates="business_types")
    filters = relationship("Filter", secondary=business_type_filters, back_populates="business_types")
    professions = relationship("Profession", secondary=business_type_professions, back_populates="business_types")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("business_types_name", "name"),
        Index("business_types_business_domain_id", "business_domain_id"),
        Index("business_types_name_active", "name", "active"),
        Index("business_types_name_active_business_domain_id", "name", "active", "business_domain_id")
    )