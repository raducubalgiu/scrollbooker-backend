from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP, func
from core.database import Base

class UserSearchHistory(Base):
    __tablename__ = "user_search_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    keyword = Column(String, nullable=False)
    count = Column(Integer, default=1)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)