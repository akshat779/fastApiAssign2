from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum

class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: RoleEnum

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class AdminBase(BaseModel):
    user_id: int

class Admin(AdminBase):
    id: int
    user: User

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    category: Optional[str] = None
    quantity: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    admin_id: Optional[int]

    class Config:
        orm_mode = True

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    total_price: float

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderItem(OrderItemBase):
    id: int
    user_id: int  # Add user_id
    order_id: int

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    total_quantity: int
    total_amount: int
    status: str

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    user_id: int
   

    class Config:
        orm_mode = True

class FavoriteBase(BaseModel):
    product_id: int

class FavoriteCreate(FavoriteBase):
    pass

class Favorite(FavoriteBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None