from sqlalchemy import Column, String, Integer, TIMESTAMP, func, Index

from models import Base

class SearchKeyword(Base):
    __tablename__ = "search_keywords"

    keyword = Column(String, primary_key=True)
    count = Column(Integer, default=1)
    last_used_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    __table__args__ = (
        Index(
            "idx_search_keywords_trgm",
            "keyword",
            postgresql_using="gin",
            postgresql_ops={"keyword": "gin_trgm_ops"}
        )
    )