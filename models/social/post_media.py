from sqlalchemy.orm import relationship

from backend.core.enums.media_type_enum import MediaTypeEnum
from backend.models import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey, Float, Index
from sqlalchemy import Enum

class PostMedia(Base):
    __tablename__ = "post_media"

    id = Column(Integer, primary_key=True)
    url = Column(Enum(MediaTypeEnum, name="media_type"), nullable=False)
    type = Column(String, nullable=False, default="photo")
    thumbnail_url = Column(String, nullable=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    order_index = Column(Integer, nullable=False, default=0)
    duration = Column(Float, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    post = relationship("Post", back_populates="media_files")

    __table_args__ = (
        Index("idx_post_id", "post_id"),
        Index("idx_post_id_order_index", "post_id", "order_index")
    )