from sqlalchemy import String, Date, ForeignKey, Enum, Text, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List
from .connection import Base
from datetime import date, datetime
from enum import Enum as PyEnum

class UserProfile(Base):
    __tablename__ = 'user_profile'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(unique=True, nullable=True)
    phone: Mapped[int | None] = mapped_column(unique=True, nullable=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    registered_date: Mapped[date] = mapped_column(Date, default=date.today)

    user_refresh: Mapped[List['UserRefresh']] = relationship(back_populates='refresh_user',
                                                             cascade='all, delete-orphan')
    user_store: Mapped[List['Store']] = relationship(back_populates='store_user',
                                                     cascade='all, delete-orphan')
    user_order: Mapped[List['Order']] = relationship(back_populates='order_user',
                                                     cascade='all, delete-orphan')

    def __repr__(self):
        return super().__repr__()

class UserRefresh(Base):
    __tablename__ = 'user_refresh'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user_profile.id', ondelete='CASCADE'), nullable=False)
    token: Mapped[str] = mapped_column(nullable=False)

    refresh_user: Mapped[UserProfile] = relationship(back_populates='user_refresh')

    def __repr__(self):
        return super().__repr__()

class CategoryChoices(str, PyEnum):
    CUSTOM = 'Custom'
    ELECTRONICS = 'Electronics'
    BEAUTY = 'Beauty'
    CLOTHING = 'Clothing'
    FOOD = 'Food'

class Store(Base):
    __tablename__ = 'store'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[CategoryChoices | None] = mapped_column(
        Enum(CategoryChoices), default=CategoryChoices.CUSTOM, nullable=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image: Mapped[str | None] = mapped_column(nullable=True)
    owner: Mapped[int] = mapped_column(ForeignKey('user_profile.id', ondelete='CASCADE'), nullable=False)
    created_date: Mapped[date] = mapped_column(Date, default=date.today)

    store_user: Mapped[UserProfile] = relationship(back_populates='user_store')
    store_product: Mapped[List['Product']] = relationship(back_populates='product_store',
                                                          cascade='all, delete-orphan')

    def __repr__(self):
        return super().__repr__()

class Product(Base):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    store: Mapped[int] = mapped_column(ForeignKey('store.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    price: Mapped[str] = mapped_column(nullable=False)
    created_date: Mapped[date] = mapped_column(Date, default=date.today)

    product_store: Mapped[Store] = relationship(back_populates='store_product')
    product_order: Mapped[List['Order']] = relationship(back_populates='order_product',
                                                        cascade='all, delete-orphan')

    def __repr__(self):
        return super().__repr__()

class StatusChoices(str, PyEnum):
    CANCEL = 'Cancel'
    CONFIRM = 'Confirm'
    PENDING = 'Pending'
    DELIVERED = 'Delivered'

class Order(Base):
    __tablename__ = 'order'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    product: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    user: Mapped[int] = mapped_column(ForeignKey('user_profile.id', ondelete='CASCADE'), nullable=False)
    status: Mapped[StatusChoices | None] = mapped_column(
        Enum(StatusChoices), default=StatusChoices.PENDING, nullable=True
    )
    ordered_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.today)

    order_product: Mapped[Product] = relationship(back_populates='product_order')
    order_user: Mapped[UserProfile] = relationship(back_populates='user_order')

    def __repr__(self):
        return super().__repr__()