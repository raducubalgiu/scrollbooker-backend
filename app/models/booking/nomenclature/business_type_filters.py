from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint
from app.models import  Base

business_type_filters = Table(
    "business_type_filters",
    Base.metadata,
    Column('business_type_id', Integer, ForeignKey('business_types.id', ondelete="CASCADE"), primary_key=True),
    Column('filter_id', Integer, ForeignKey('filters.id', ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("business_type_id", "filter_id", name="uq_business_type_filter")
)