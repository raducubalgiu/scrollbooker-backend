from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from models import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)

    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    data = Column(JSONB, nullable=True)
    message = Column(String(200), nullable=True)

    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])