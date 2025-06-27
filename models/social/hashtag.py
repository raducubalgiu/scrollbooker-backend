from models import Base
from sqlalchemy import Integer,String, TIMESTAMP, Column, func

class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True, index=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    #posts = relationship("PostHashtag", back_populates="hashtag", cascade="all, delete-orphan")

    def __init__(self, name: str):
        self.name = name.lower()



