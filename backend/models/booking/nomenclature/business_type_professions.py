from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint
from backend.models import  Base

business_type_professions = Table(
    "business_type_professions",
    Base.metadata,
    Column('business_type_id', Integer, ForeignKey('business_types.id', ondelete="CASCADE"), primary_key=True),
    Column('profession_id', Integer, ForeignKey('professions.id', ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("business_type_id", "profession_id", name="uq_business_type_professions")
)