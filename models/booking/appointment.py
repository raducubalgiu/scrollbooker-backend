from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, func, String, Enum, Index, Boolean, DECIMAL
from sqlalchemy.orm import relationship

from core.enums.appointment_channel_enum import AppointmentChannelEnum
from core.enums.appointment_status_enum import AppointmentStatusEnum
from models import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    end_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)

    customer_fullname = Column(String(50), nullable=False)

    status = Column(Enum(AppointmentStatusEnum), default=AppointmentStatusEnum.IN_PROGRESS, nullable=False, index=True)
    channel = Column(Enum(AppointmentChannelEnum), default=AppointmentChannelEnum.SCROLL_BOOKER, nullable=False, index=True)

    total_price = Column(DECIMAL, nullable=False)
    total_duration = Column(Integer, nullable=False)

    is_blocked = Column(Boolean, nullable=False, default=False)
    message = Column(String(100), nullable=True)

    payment_currency_id = Column(Integer, ForeignKey("currencies.id", ondelete="CASCADE"), nullable=False)
    exchange_rate_source = Column(String(32), nullable=True)
    exchange_rate_timestamp = Column(TIMESTAMP(timezone=True), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relations
    user = relationship("User", foreign_keys=[user_id], back_populates="appointments_user")
    customer = relationship("User", foreign_keys=[customer_id], back_populates="appointments_customer")
    business = relationship("Business", back_populates="appointments")
    products = relationship("AppointmentProduct", back_populates="appointment")

    __table_args__ = (
        Index("idx_appointments_start_date", "start_date"),
        Index("idx_appointments_end_date", "end_date"),
        Index("idx_appointments_user_id", "user_id"),
        Index("idx_appointments_customer_id", "customer_id"),
        Index("idx_appointments_business_id", "business_id"),
        Index("idx_appointments_status", "status"),
        Index("idx_appointments_channel", "channel"),

        Index("idx_appointments_compound_user", "start_date", "end_date", "user_id"),
        Index("idx_appointments_compound_customer", "start_date", "end_date", "customer_id"),
        Index("idx_appointments_compound_user_status", "start_date", "end_date", "user_id", "status")
    )

