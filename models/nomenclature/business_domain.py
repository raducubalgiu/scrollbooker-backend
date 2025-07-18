from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Boolean, Index
from sqlalchemy.orm import relationship

from models import Base

class BusinessDomain(Base):
    __tablename__ = "business_domains"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    short_name = Column(String(50), nullable=False, index=True)
    active = Column(Boolean, nullable=False, default=True, index=True)

    business_types = relationship("BusinessType", back_populates="business_domain")
    professions = relationship("Profession", back_populates="business_domain")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("business_domains_name", "name"),
        Index("business_domains_short_name", "short_name"),
        Index("business_domains_name_active", "name", "active"),
    )