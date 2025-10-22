from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from models import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey, Boolean, ARRAY, Text, BigInteger, Index

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)

    business_type_id = Column(Integer, ForeignKey("business_types.id", ondelete="CASCADE"), nullable=False, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    business_owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Just for Video Review Posts
    employee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    is_video_review = Column(Boolean, nullable=False, default=False)
    video_review_message = Column(String(255), nullable=True)
    rating = Column(Integer, nullable=True)

    bookable = Column(Boolean, nullable=False, default=True)
    is_last_minute = Column(Boolean, nullable=False, default=False)
    last_minute_end = Column(TIMESTAMP(timezone=True), nullable=True)

    has_fixed_slots = Column(Boolean, nullable=False, default=False)
    fixed_slots = Column(JSONB, nullable=True)

    hashtags = Column(ARRAY(Text), nullable=True)
    mentions = Column(ARRAY(BigInteger), nullable=True)

    like_count = Column(Integer, nullable=False, default=0)
    repost_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    bookmark_count = Column(Integer, nullable=False, default=0)
    bookings_count = Column(Integer, nullable=False, default=0)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relations
    likes = relationship("Like", back_populates="post")
    bookmark_posts = relationship("BookmarkPost", back_populates="post")
    reposts = relationship("Repost", back_populates="post")

    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="user_posts"
    )
    employee = relationship(
        "User",
        foreign_keys=[employee_id],
        back_populates="employee_posts"
    )
    business_owner = relationship(
        "User",
        foreign_keys=[business_owner_id],
        back_populates="business_owner_posts"
    )
    product = relationship("Product", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete")
    media_files = relationship(
        "PostMedia",
        back_populates="post",
        cascade="all, delete",
        order_by="PostMedia.order_index"
    )

    __table_args__ = (
        Index("idx_posts_user_id", "user_id"),
        Index("idx_posts_business_id", "business_id"),
        Index("idx_posts_business_owner_id", "business_owner_id"),
        Index("idx_posts_business_type_id", "business_type_id"),
        Index("idx_posts_employee_id", "employee_id"),
        Index("idx_posts_product_id", "product_id"),
        Index("idx_posts_created_at", "created_at"),


        Index("idx_posts_query_compound",
          "user_id",
                      "business_id",
                      "business_owner_id",
                      "business_type_id",
                      "employee_id",
                      "product_id",
                      "created_at"
              )

        # -- Index for video reviews employees
        # CREATE INDEX IF NOT EXISTS idx_posts_vr_employee_created_desc
        # ON POSTS (employee_id, created_at DESC)
        # WHERE is_video_review = TRUE;

        # -- Index for video reviews business_owner
        # CREATE INDEX IF NOT EXISTS idx_posts_vr_owner_created_desc
        # ON POSTS (business_owner_id, created_at DESC)
        # WHERE is_video_review = TRUE;
    )