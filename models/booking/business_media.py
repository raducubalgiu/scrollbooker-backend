from sqlalchemy.orm import relationship

from core.enums.media_type_enum import MediaTypeEnum
from models import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey, Float, Index
from sqlalchemy import Enum

class BusinessMedia(Base):
    __tablename__ = "business_media"

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    type = Column(Enum(MediaTypeEnum, name="media_type"), nullable=False, default="video")
    thumbnail_url = Column(String, nullable=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)

    order_index = Column(Integer, nullable=False, default=0)
    duration = Column(Float, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    business = relationship("Business", back_populates="media_files")

    __table_args__ = (
        Index("idx_media_business_id", "business_id"),
        Index("idx_business_id_order_index", "business_id", "order_index")
    )