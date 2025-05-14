from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint
from backend.models import  Base

product_sub_filters = Table(
    "product_sub_filters",
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id', ondelete="CASCADE"), primary_key=True),
    Column('sub_filter_id', Integer, ForeignKey('sub_filters.id', ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("product_id", "sub_filter_id", name="uq_product_sub_filter")
)