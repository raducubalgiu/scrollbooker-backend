from sqlalchemy import Column, Integer, String, Time, ForeignKey, UniqueConstraint, Index, Interval
from sqlalchemy.orm import relationship
from app.models import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String, nullable=False, index=True) # This will be an enum later
    start_time = Column(Time(timezone=True), nullable=True)
    end_time = Column(Time(timezone=True), nullable=True)
    time_offset = Column(Interval, nullable=False)
    day_week_index = Column(Integer, nullable=False)

    # User with role Business or Employee
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="schedules")
    business = relationship("Business", back_populates="schedules")

    __table_args__ = (
        UniqueConstraint("user_id", "day_of_week", name="unique_user_day"),
        Index("idx_start_time", "start_time"),
        Index("idx_end_time", "end_time"),
        Index("idx_user_id_day_of_week", "user_id", "day_of_week"),
        Index("idx_user_id_start_time_end_time_day_of_week", "user_id", "start_time", "end_time", "day_of_week"),
        Index("idx_business_id_start_time_end_time_day_of_week", "business_id", "start_time", "end_time", "day_of_week")
    )



