from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint, Index, TIMESTAMP, func
from sqlalchemy.orm import relationship

from backend.models import Base

class EmploymentRequest(Base):
    __tablename__ = "employment_requests"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    employer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    profession_id = Column(Integer, ForeignKey("professions.id", ondelete="SET NULL"))

    ended_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    consent_id = Column(Integer, ForeignKey("consents.id"), nullable=False)

    start_date = Column(TIMESTAMP(timezone=True), nullable=True)
    end_date = Column(TIMESTAMP(timezone=True), nullable=True)
    status = Column(String, nullable=False, default='pending')

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    employee = relationship("User", foreign_keys=[employee_id], back_populates="employment_requests_as_employee")
    employer = relationship('User', foreign_keys=[employer_id], back_populates="employment_requests_as_employer")
    business = relationship('Business', back_populates="employment_requests")
    profession = relationship("Profession", back_populates="employment_requests")


    __table_args__ = (
        UniqueConstraint('employee_id', 'employer_id', 'business_id', name='uix_employee_employer_business'),
        Index('idx_employee_id', 'employee_id'),
        Index('idx_employer_id', 'employer_id'),
        Index('idx_business_id', 'business_id'),
        Index('idx_ended_by', 'ended_by'),
        Index('idx_status', 'status')
    )
