from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint
from app.models import  Base

service_business_types = Table(
    "service_business_types",
    Base.metadata,
    Column('service_id', Integer, ForeignKey('services.id', ondelete="CASCADE"), primary_key=True),
    Column('business_type_id', Integer, ForeignKey('business_types.id', ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("service_id", "business_type_id", name="uq_service_business_type")
)

