from sqlalchemy import Table, Column, Integer, ForeignKey
from models import  Base

business_services = Table(
    "business_services",
    Base.metadata,
    Column('business_id', Integer, ForeignKey('businesses.id', ondelete="CASCADE"), primary_key=True),
    Column('service_id', Integer, ForeignKey('services.id', ondelete="CASCADE"), primary_key=True)
)