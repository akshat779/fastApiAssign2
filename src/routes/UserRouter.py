from ..repository import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..utils.database import get_db
from ..schemas import schemas
from typing import List
from ..utils.dependencies import is_self_or_admin
from ..models import models
from ..utils.oauth import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

@router.get("/", response_model=List[schemas.User])
def getAll(db: Session = Depends(get_db)):
    return User.getAll(db)

@router.post("/", response_model=schemas.User)
def create(request: schemas.UserCreate, db: Session = Depends(get_db)):
    return User.create(request, db)

@router.get("/{id}", response_model=schemas.User)
def show(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(is_self_or_admin)):
    return User.show(id, db)

@router.put("/{id}", response_model=str)
def update(id: int, request: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(is_self_or_admin)):
    return User.update(id, request, db)

@router.get("/{user_id}/favorites", response_model=List[schemas.Product])
def get_favorite_products(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(is_self_or_admin)):
    return User.get_favorite_products(user_id, db)

@router.get("/{user_id}/orders", response_model=List[schemas.Order])
def get_user_orders(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(is_self_or_admin)):
    return User.get_user_orders(user_id, db)

@router.delete("/{id}", response_model=str)
def delete(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(is_self_or_admin)):
    return User.delete(id, db)

@router.post("/order-items/", response_model=schemas.OrderItem)
def create_order_item(request: schemas.OrderItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return User.create_order_item(current_user.id, request, db)

@router.get("/order-items/{id}", response_model=schemas.OrderItem)
def get_order_item(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return User.get_order_item(current_user.id, id, db)

@router.put("/order-items/{id}", response_model=schemas.OrderItem)
def update_order_item(id: int, request: schemas.OrderItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return User.update_order_item(current_user.id, id, request, db)

@router.delete("/order-items/{id}", response_model=str)
def delete_order_item(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return User.delete_order_item(current_user.id, id, db)