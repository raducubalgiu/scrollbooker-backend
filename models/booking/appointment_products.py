from sqlalchemy import Column, Integer, ForeignKey, Index, DECIMAL, UniqueConstraint, String
from sqlalchemy.orm import relationship

from core.database import Base

class AppointmentProduct(Base):
    __tablename__ = "appointment_products"

    id = Column(Integer, primary_key=True)

    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)

    name = Column(String(100), nullable=False)
    price = Column(DECIMAL, nullable=False)
    price_with_discount = Column(DECIMAL, nullable=False)
    discount = Column(DECIMAL, nullable=False)
    duration = Column(DECIMAL, nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)

    converted_price_with_discount = Column(DECIMAL, nullable=False)
    exchange_rate = Column(DECIMAL, nullable=True)

    appointment = relationship("Appointment", back_populates="products")

    __table_args__ = (
        UniqueConstraint("appointment_id", "product_id", name="uq_appointment_product"),
        Index("idx_app_products_appointment", "appointment_id"),
        Index("idx_app_products_product", "product_id"),
        Index("idx_app_products_compound", "appointment_id", "product_id"),
    )