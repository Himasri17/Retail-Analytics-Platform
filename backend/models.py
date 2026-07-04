"""
models.py
---------
SQLAlchemy ORM model mirroring the Superstore schema (one row per order line-item).
"""

from sqlalchemy import Column, Date, Float, Integer, String

from database import Base


class OrderLine(Base):
    __tablename__ = "orders"

    row_id = Column("row_id", Integer, primary_key=True, autoincrement=False)
    order_id = Column("order_id", String, index=True)
    order_date = Column("order_date", Date, index=True)
    ship_date = Column("ship_date", Date)
    ship_mode = Column("ship_mode", String)
    customer_id = Column("customer_id", String, index=True)
    customer_name = Column("customer_name", String)
    segment = Column("segment", String)
    country = Column("country", String)
    city = Column("city", String)
    state = Column("state", String)
    postal_code = Column("postal_code", String)
    region = Column("region", String, index=True)
    product_id = Column("product_id", String, index=True)
    category = Column("category", String, index=True)
    sub_category = Column("sub_category", String, index=True)
    product_name = Column("product_name", String)
    sales = Column("sales", Float)
    quantity = Column("quantity", Integer)
    discount = Column("discount", Float)
    profit = Column("profit", Float)
