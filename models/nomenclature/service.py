from sqlalchemy import Column, Integer, Boolean, String, TIMESTAMP, func, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import relationship
from models import Base
from models.booking.business_services import business_services
from models.nomenclature.service_business_types import service_business_types

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True)
    keywords = Column(JSONB, nullable=True, server_default="[]", index=True)
    active = Column(Boolean, default=True, index=True)

    business_domain_id = Column(Integer, ForeignKey("business_domains.id", ondelete="CASCADE"), nullable=False, index=True)
    service_domain_id = Column(Integer, ForeignKey("service_domains.id", ondelete="CASCADE"), index=True)

    search_vector = Column(TSVECTOR)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relations
    businesses = relationship("Business", secondary=business_services, back_populates="services")
    products = relationship("Product", back_populates="service", cascade="all, delete")
    reviews = relationship("Review", back_populates="service")
    service_domain = relationship("ServiceDomain", back_populates="services")
    business_types = relationship("BusinessType", secondary=service_business_types, back_populates="services")

    __table_args__ = (
        Index("idx_services_name", "name"),
        Index("idx_services_business_domain_id", "business_domain_id"),
        Index("idx_services_service_domain_id", "service_domain_id"),
        Index("idx_services_keywords_active", "name", "keywords", "active"),
        Index("idx_services_search_vector", "search_vector", postgresql_using="gin")
    )