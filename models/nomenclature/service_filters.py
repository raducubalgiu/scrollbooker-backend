from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Table

from core.database import Base

service_filters = Table(
    "service_filters",
    Base.metadata,
    Column('service_id', Integer, ForeignKey('services.id', ondelete="CASCADE"), primary_key=True),
    Column('filter_id', Integer, ForeignKey('filters.id', ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("service_id", "filter_id", name="uq_service_filter")
)