from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey, Index, Boolean
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=True)
    city = Column(String(100))
    state = Column(String(100))
    region = Column(String(50), index=True)
    segment = Column(String(50), index=True)

    orders = relationship("Order", back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(200), nullable=False)
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), index=True)
    order_date = Column(Date, index=True, nullable=False)
    region = Column(String(50), index=True)
    salesperson = Column(String(120))
    order_status = Column(String(30), default="Completed")

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    revenue = Column(Float, nullable=False, index=True)
    profit = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


Index("ix_orders_date_region_composite", Order.order_date, Order.region)


class UploadJob(Base):
    """Tracks the status of an uploaded file as it moves through the pipeline."""
    __tablename__ = "upload_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    filename = Column(String(255))
    status = Column(String(30), default="uploaded")  # uploaded, validating, cleaning, analyzing, complete, failed
    rows_processed = Column(Integer, default=0)
    error_message = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
