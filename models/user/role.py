from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, func, Enum, Index
from sqlalchemy.orm import relationship

from core.enums.role_enum import RoleEnum
from models import Base
from models.user.role_permissions import role_permissions

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(RoleEnum), unique=True, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship with users - ONE TO MANY
    users = relationship("User", back_populates="role")

    # Relationship with permissions - MANY TO MANY
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

    __table_args__ = (
        Index("idx_role_name", "name"),
        Index("idx_active", "active"),
    )