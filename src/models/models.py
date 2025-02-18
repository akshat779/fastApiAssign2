# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DECIMAL, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class RoleEnum(enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    password = Column(Text, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    orders = relationship('Order', back_populates='user')
    favorites = relationship('Favorite', back_populates='user')
    admin = relationship('Admin', uselist=False, back_populates='user')
    order_items = relationship('OrderItem', back_populates='user')  # Add relationship

class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    user = relationship('User', back_populates='admin')
    products = relationship('Product', back_populates='admin')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey('admins.id', ondelete='SET NULL'))
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    category = Column(String)
    quantity = Column(Integer, nullable=False)

    admin = relationship('Admin', back_populates='products')
    order_items = relationship('OrderItem', back_populates='product')
    favorites = relationship('Favorite', back_populates='product')

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    total_quantity = Column(Integer)
    total_amount = Column(DECIMAL(10, 2))
    status = Column(String)

    user = relationship('User', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order')

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))  # Add user_id
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)

    user = relationship('User', back_populates='order_items')  # Relationship with User
    order = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')

class Favorite(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'))

    user = relationship('User', back_populates='favorites')
    product = relationship('Product', back_populates='favorites')