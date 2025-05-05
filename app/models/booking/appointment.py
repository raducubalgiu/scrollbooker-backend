from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, func, String, UniqueConstraint, Index, Boolean, Float, \
    DECIMAL
from sqlalchemy.orm import relationship
from app.models import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    end_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    block_message = Column(String(50), nullable=True)
    status = Column(String, default='in_progress', nullable=False, index=True) #finished - in_progress
    channel = Column(String, default='scroll_booker', nullable=False, index=True) #scroll_booker - own_client
    instant_booking = Column(Boolean, nullable=False)
    is_blocked = Column(Boolean, nullable=False, default=False)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)

    customer_username = Column(String(50), nullable=False)
    service_name = Column(String(50), nullable=False)
    product_price = Column(DECIMAL, nullable=False)

    currency = Column(String(50), nullable=False) # this should be an enum later
    exchange_rate = Column(DECIMAL, nullable=False, default=1)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relations
    customer = relationship("User", foreign_keys=[customer_id], back_populates="appointments_customer")
    business = relationship("Business", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    product = relationship("Product", back_populates="appointments")
    user = relationship("User", foreign_keys=[user_id], back_populates="appointments_user")

    __table_args__ = (
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

