from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from models import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey, Boolean, ARRAY, Text, BigInteger, Index, \
    DECIMAL

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    business_type_id = Column(Integer, ForeignKey("business_types.id", ondelete="CASCADE"), nullable=False, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="SET NULL"), nullable=False)
    instant_booking = Column(Boolean, nullable=False, default=True, index=True)

    product_name = Column(String(100), nullable=False)
    product_description = Column(String(200), nullable=False)
    product_duration = Column(Integer, nullable=False)
    product_price = Column(DECIMAL, nullable=False)
    product_price_with_discount = Column(DECIMAL, nullable=False)
    product_discount = Column(DECIMAL, nullable=False)
    product_currency = Column(String(3), nullable=False)

    bookable = Column(Boolean, nullable=False, default=True)
    is_last_minute = Column(Boolean, nullable=False, default=False)
    last_minute_end = Column(TIMESTAMP(timezone=True), nullable=True)
    has_fixed_slots = Column(Boolean, nullable=False, default=False)
    fixed_slots = Column(JSONB, nullable=True)

    hashtags = Column(ARRAY(Text), nullable=True)
    mentions = Column(ARRAY(BigInteger), nullable=True)

    like_count = Column(Integer, nullable=False, default=0)
    share_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    bookmark_count = Column(Integer, nullable=False, default=0)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relations
    likes = relationship("Like", back_populates="post")
    bookmark_posts = relationship("BookmarkPost", back_populates="post")
    reposts = relationship("Repost", back_populates="post")
    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete")
    media_files = relationship(
        "PostMedia",
        back_populates="post",
        cascade="all, delete",
        order_by="PostMedia.order_index"
    )

    __table_args__ = (
        Index("idx_post_user", "user_id"),
        Index("idx_post_product_id", "product_id"),
        Index("idx_post_created_at", "created_at"),
        Index("idx_post_is_last_minute", "is_last_minute"),


        Index("idx_post_last_minute_created", "is_last_minute", "created_at"),
        Index("idx_instant_booking_created", "instant_booking", "created_at"),
        Index("idx_business_type_id_created", "business_type_id", "created_at")
    )