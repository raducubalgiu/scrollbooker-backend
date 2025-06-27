from sqlalchemy import Column, Integer, String, Time, ForeignKey, UniqueConstraint, Index, Enum
from sqlalchemy.orm import relationship

from core.enums.day_of_week_enum import DayOfWeekEnum
from models import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Enum(DayOfWeekEnum), nullable=False, index=True)
    day_week_index = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)

    # User with role Business or Employee
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="schedules")
    business = relationship("Business", back_populates="schedules")

    __table_args__ = (
        UniqueConstraint("user_id", "day_of_week", name="unique_user_day"),
        UniqueConstraint("user_id", "day_week_index", name="unique_user_day_week_index"),
        Index("idx_start_time", "start_time"),
        Index("idx_end_time", "end_time"),
        Index("idx_user_id_day_of_week", "user_id", "day_of_week"),
        Index("idx_user_id_start_time_end_time_day_of_week", "user_id", "start_time", "end_time", "day_of_week"),
        Index("idx_business_id_start_time_end_time_day_of_week", "business_id", "start_time", "end_time", "day_of_week")
    )



