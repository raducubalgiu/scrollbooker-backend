from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from .business_services import business_services
from app.models import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True)
    coordinates = Column(Geometry("POINT", srid=4326), nullable=False, unique=True) # SRID 4326 (GPS coordinates)
    timezone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    description = Column(String, nullable=True)
    has_employees = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Foreign key
    owner_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_type_id = Column(Integer, ForeignKey("business_types.id"), nullable=False)

    business_type = relationship("BusinessType", back_populates="businesses")
    business_owner = relationship("User", back_populates="owner_business", foreign_keys=[owner_id])
    employees = relationship("User", back_populates="employee_business", foreign_keys="User.employee_business_id")
    services = relationship("Service", secondary=business_services, back_populates="businesses")
    schedules = relationship("Schedule", back_populates="business")
    products = relationship("Product", back_populates="business", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="business")
    employment_requests = relationship("EmploymentRequest", back_populates="business")