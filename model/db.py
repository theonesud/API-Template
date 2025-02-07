from contextlib import asynccontextmanager
from datetime import time
from functools import partial
from typing import AsyncGenerator

from sqlalchemy import (
    DECIMAL,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from config import app_logger, settings

Base = declarative_base()
NotNullColumn = partial(Column, nullable=False)


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = NotNullColumn(String(255))
    about = NotNullColumn(Text)
    calling_phone_numbers = NotNullColumn(String(255))
    whatsapp_phone_number = NotNullColumn(String(255))
    created_at = NotNullColumn(DateTime)
    updated_at = Column(DateTime)

    users = relationship("User", back_populates="company")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = NotNullColumn(String(255), unique=True)
    company_id = NotNullColumn(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    deleted = NotNullColumn(Boolean, default=False)
    created_at = NotNullColumn(DateTime)
    updated_at = Column(DateTime)

    sales_orders = relationship("SalesOrder", back_populates="customer")
    company = relationship("Company", back_populates="users")
    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = NotNullColumn(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    login_time = NotNullColumn(DateTime)
    deleted = NotNullColumn(Boolean, default=False)

    user = relationship("User", back_populates="sessions")


class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True)
    name = NotNullColumn(String(255))
    description = Column(Text)
    price = NotNullColumn(DECIMAL)
    category = Column(String(255))
    created_at = NotNullColumn(DateTime)
    updated_at = Column(DateTime)
    deleted = Column(Boolean, default=False)

    inventory = relationship(
        "Inventory",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )
    order_items = relationship(
        "OrderItem", back_populates="product", cascade="all, delete-orphan"
    )


class SalesOrder(Base):
    __tablename__ = "sales_orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_date = NotNullColumn(DateTime)
    customer_id = NotNullColumn(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    total_amount = Column(DECIMAL)
    status = NotNullColumn(
        String(255), default="pending"
    )  # pending, processing, shipped, delivered
    created_at = NotNullColumn(DateTime)
    updated_at = Column(DateTime)
    deleted = Column(Boolean, default=False)

    customer = relationship("User", back_populates="sales_orders")
    order_items = relationship(
        "OrderItem", back_populates="sales_order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = NotNullColumn(Integer, ForeignKey("sales_orders.id", ondelete="CASCADE"))
    product_id = NotNullColumn(String, ForeignKey("products.id", ondelete="CASCADE"))
    quantity = NotNullColumn(Integer)
    price = NotNullColumn(DECIMAL)  # Price at the time of order
    created_at = NotNullColumn(DateTime)
    updated_at = Column(DateTime)
    deleted = Column(Boolean, default=False)

    sales_order = relationship("SalesOrder", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")


class Inventory(Base):
    __tablename__ = "inventories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = NotNullColumn(
        String, ForeignKey("products.id", ondelete="CASCADE"), unique=True
    )
    quantity_in_stock = NotNullColumn(Integer, default=0)
    last_stock_update = Column(DateTime)
    created_at = NotNullColumn(DateTime)
    updated_at = Column(DateTime)
    deleted = Column(Boolean, default=False)

    product = relationship("Product", back_populates="inventory")


engine = create_async_engine(
    settings.ASYNCPG_URL,
    future=True,
    echo=True,
    pool_size=20,
    max_overflow=10,
    connect_args={"server_settings": {"statement_timeout": "10000"}},
)
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        async with session.begin():
            try:
                yield session
                await session.commit()
            except DBAPIError as ex:
                await session.rollback()
                app_logger.debug("Session timeout...")
                raise ex
            except SQLAlchemyError as ex:
                await session.rollback()
                app_logger.debug("Session rollback...")
                raise ex
            finally:
                await session.close()
