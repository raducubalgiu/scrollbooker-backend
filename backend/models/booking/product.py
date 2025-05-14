from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func, Index, DECIMAL
from sqlalchemy.orm import relationship

from backend.models import Base
from backend.models.booking.product_sub_filters import product_sub_filters

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String, nullable=True)
    duration = Column(Integer, nullable=False, index=True)
    price = Column(DECIMAL, nullable=False, index=True)
    price_with_discount = Column(DECIMAL, nullable=True)
    discount = Column(DECIMAL, nullable=False, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Foreign keys
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)

    # Relations
    service = relationship("Service", back_populates="products")
    business = relationship("Business", back_populates="products")
    user = relationship("User", back_populates="products")
    appointments = relationship("Appointment", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    currency = relationship('Currency', back_populates="products")
    sub_filters = relationship("SubFilter", secondary=product_sub_filters, back_populates="products")

    __table_args__ = (
        Index("idx_products_name", "name"),
        Index("idx_products_duration", "duration"),
        Index("idx_products_price", "price"),
        Index("idx_products_discount", "discount"),
        Index("idx_products_service_id", "service_id"),
        Index("idx_products_business_id", "business_id"),
        Index("idx_products_user_id", "user_id"),
        Index("idx_products_service_id_business_id", "service_id", "business_id"),
        Index("idx_products_service_id_user_id", "service_id", "user_id"),
        Index("idx_products_service_id_business_id_user_id", "service_id", "business_id", "user_id"),
    )