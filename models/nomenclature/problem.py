from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey

from backend.core.database import Base


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key = True)
    text = Column(String(500), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)