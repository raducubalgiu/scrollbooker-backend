from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.models import Base

class UserCounters(Base):
    __tablename__ = "user_counters"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    followings_count = Column(Integer, default=0, nullable=False)
    followers_count = Column(Integer, default=0, nullable=False)
    products_count = Column(Integer, default=0, nullable=False)
    posts_count = Column(Integer, default=0, nullable=False)
    ratings_count = Column(Integer, default=0, nullable=False)
    ratings_average = Column(Float, default=5, nullable=False)

    # Relationship with user - ONE TO ONE
    user = relationship("User", back_populates="counters", uselist=False)