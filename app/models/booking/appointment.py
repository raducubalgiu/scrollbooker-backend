from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, func, String, UniqueConstraint, Index, Boolean
from sqlalchemy.orm import relationship
from app.models import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    end_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    status = Column(String, default='in_progress', nullable=False, index=True)
    channel = Column(String, default='closer_app', nullable=False, index=True)
    instant_booking = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Foreign keys
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=False, index=True)

    # User with role Business or Employee
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    # Relations
    customer = relationship("User", foreign_keys=[customer_id], back_populates="appointments_customer")
    business = relationship("Business", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    product = relationship("Product", back_populates="appointments")
    user = relationship("User", foreign_keys=[user_id], back_populates="appointments_user")

    __table_args__ = (
        UniqueConstraint("user_id", "created_at", name="unique_user_created_at"),
        Index("idx_appointments_customer_id", "customer_id"),
        Index("idx_appointments_business_id", "business_id"),
        Index("idx_appointments_service_id", "service_id"),
        Index("idx_appointments_product_id", "product_id"),
        Index("idx_appointments_start_date", "start_date"),
        Index("idx_appointments_end_date", "end_date"),
        Index("idx_appointments_status", "status"),
        Index("idx_appointments_channel", "channel"),
        Index("idx_appointments_start_date_end_date_status", "start_date", "end_date", "status"),
        Index("idx_appointments_start_date_end_date_business_id_status", "start_date", "end_date", "business_id", "status"),
        Index("idx_appointments_start_date_end_date_user_id_status", "start_date", "end_date", "user_id", "status"),
    )

