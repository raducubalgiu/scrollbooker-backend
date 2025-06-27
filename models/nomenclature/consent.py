from sqlalchemy import Column, Integer, String, TEXT, TIMESTAMP, func, Index
from models import Base

class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    title = Column(String(50), nullable=False)
    text = Column(TEXT, nullable=False)
    version = Column(String(50), default="v1")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_consents_name", "name"),
    )