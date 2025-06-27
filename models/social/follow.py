from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from models import Base

class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    followee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followee = relationship("User", foreign_keys=[followee_id], back_populates="followers")

    __table__args = (
        Index("idx_follows_follower", "follower_id"),
        Index("idx_follows_followee", "followee_id"),
        Index("idx_follows_follower_followee", "follower_id", "followee_id"),
        UniqueConstraint("follower_id", "followee_id", name="unique_follows"),
    )
