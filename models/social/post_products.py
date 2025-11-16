from sqlalchemy import Column, Integer, ForeignKey, String, DECIMAL, UniqueConstraint, Index

from core.database import Base

class PostProduct(Base):
    __tablename__ = "post_products"

    id = Column(Integer, primary_key=True)

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)

    name = Column(String(100), nullable=False)
    price = Column(DECIMAL, nullable=False)
    price_with_discount = Column(DECIMAL, nullable=False)
    discount = Column(DECIMAL, nullable=False)
    duration = Column(DECIMAL, nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)

    converted_price_with_discount = Column(DECIMAL, nullable=False)
    exchange_rate = Column(DECIMAL, nullable=True)

    __table_args__ = (
        UniqueConstraint("post_id", "product_id", name="uq_post_product"),
        Index("idx_app_post_products_appointment", "post_id"),
        Index("idx_app_post_products_product", "product_id"),
        Index("idx_app_post_products_compound", "post_id", "product_id"),
    )