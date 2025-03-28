from sqlalchemy.orm import relationship
from app.models import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey

class PostMedia(Base):
    __tablename__ = "post_media"

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    type = Column(String, nullable=False, default="photo")
    thumbnail_url = Column(String, nullable=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    post = relationship("Post", back_populates="media_files")