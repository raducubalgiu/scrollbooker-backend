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
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    currency_id = Column(Integer, ForeignKey("currencies.id", ondelete="CASCADE"), index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=True, index=True)

    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    product_name = Column(String(100), nullable=False)
    product_full_price = Column(DECIMAL, nullable=False)
    product_price_with_discount = Column(DECIMAL, nullable=False)
    product_discount = Column(DECIMAL, nullable=False, default=0)
    product_duration = Column(Integer, nullable=True)
    exchange_rate = Column(DECIMAL, nullable=False, default=1)
    message = Column(String(100), nullable=True)

    customer_fullname = Column(String(50), nullable=False)
    service_name = Column(String(50), nullable=False)

    status = Column(Enum(AppointmentStatusEnum), default=AppointmentStatusEnum.IN_PROGRESS, nullable=False, index=True)  # finished - in_progress
    channel = Column(Enum(AppointmentChannelEnum), default=AppointmentChannelEnum.SCROLL_BOOKER, nullable=False, index=True)  # scroll_booker - own_client
    instant_booking = Column(Boolean, nullable=False, default=True)
    is_blocked = Column(Boolean, nullable=False, default=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relations
    currency = relationship("Currency", back_populates="appointments")
    customer = relationship("User", foreign_keys=[customer_id], back_populates="appointments_customer")
    business = relationship("Business", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    product = relationship("Product", back_populates="appointments")
    user = relationship("User", foreign_keys=[user_id], back_populates="appointments_user")

    __table_args__ = (
        Index("idx_appointments_start_date", "start_date"),
        Index("idx_appointments_end_date", "end_date"),
        Index("idx_appointments_customer_id", "customer_id"),
        Index("idx_appointments_business_id", "business_id"),
        Index("idx_appointments_service_id", "service_id"),
        Index("idx_appointments_product_id", "product_id"),
        Index("idx_appointments_currency_id", "currency_id"),
        Index("idx_appointments_status", "status"),
        Index("idx_appointments_channel", "channel"),

        Index("idx_appointments_start_date_end_date_user_id", "start_date", "end_date", "user_id")
    )

