from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func, Index
from sqlalchemy.orm import relationship

from backend.models import Base
from backend.models.booking.nomenclature.business_type_professions import business_type_professions

class Profession(Base):
    __tablename__ = "professions"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    active = Column(Boolean, nullable=False, default=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    business_types = relationship("BusinessType", secondary=business_type_professions, back_populates="professions")
    employment_requests = relationship("EmploymentRequest", back_populates="profession")

    __table_args__ = (
        Index("profession_name", "name"),
    )