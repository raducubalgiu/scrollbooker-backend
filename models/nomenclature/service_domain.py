from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Index
from sqlalchemy.orm import relationship

from models import Base

class ServiceDomain(Base):
    __tablename__ = "service_domains"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    services = relationship("Service", back_populates="service_domain")

    __table_args__ = (
        Index("service_domains_name", "name"),
    )