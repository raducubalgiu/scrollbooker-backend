from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Index, Boolean
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from core.database import Base

class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True)
    name = Column(String(3), nullable=False, unique=True, index=True)
    active= Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    products = relationship('Product', back_populates="currency")
    users_assoc = relationship("UserCurrency", back_populates="currency")
    users = association_proxy("users_assoc", "user")

    __table_args__ = (
        Index("idx_currencies_name", "name"),
    )