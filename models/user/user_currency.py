from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func, Boolean, Index
from sqlalchemy.orm import relationship

from core.database import Base

class UserCurrency(Base):
    __tablename__ = "user_currencies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    active = Column(Boolean, default=True)

    added_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    removed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="currencies_assoc")
    currency = relationship("Currency", back_populates="users_assoc")

    __table_args__ = (
        Index("idx_currencies_user_id", "user_id"),
    )
