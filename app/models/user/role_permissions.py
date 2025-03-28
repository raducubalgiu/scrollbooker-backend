from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models import  Base

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete="CASCADE"), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete="CASCADE"), primary_key=True)
)