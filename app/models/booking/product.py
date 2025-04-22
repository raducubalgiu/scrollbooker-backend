from sqlalchemy import Column, Integer, Float, String, ForeignKey, TIMESTAMP, func, Index
from sqlalchemy.orm import relationship

from app.models import Base
from app.models.booking.product_sub_filters import product_sub_filters

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    duration = Column(Integer, nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)
    price_with_discount = Column(Float, nullable=True)
    discount = Column(Float, nullable=False, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Foreign keys
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)

    # User with role Business or Employee
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    # Relations
    service = relationship("Service", back_populates="products")
    business = relationship("Business", back_populates="products")
    user = relationship("User", back_populates="products")
    appointments = relationship("Appointment", back_populates="product")
    reviews = relationship("Review", back_populates="product")
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