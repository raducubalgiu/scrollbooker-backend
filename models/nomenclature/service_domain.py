from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Index, ForeignKey
from sqlalchemy.orm import relationship

from models import Base

class ServiceDomain(Base):
    __tablename__ = "service_domains"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    business_domain_id = Column(Integer, ForeignKey("business_domains.id", ondelete="CASCADE"), nullable=False)

    services = relationship("Service", back_populates="service_domain")
    business_domain = relationship("BusinessDomain", back_populates="service_domains")

    __table_args__ = (
        Index("service_domains_name", "name"),
    )