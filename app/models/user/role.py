from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.models import Base
from app.models.user.role_permissions import role_permissions

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship with users - ONE TO MANY
    users = relationship("User", back_populates="role")

    # Relationship with permissions - MANY TO MANY
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")