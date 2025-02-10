from ..models import models
from ..schemas import schemas
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..utils.database import get_db
from fastapi import Depends
from ..utils.hashing import hash_password



def getAll(db:Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

def create(request: schemas.UserCreate, db:Session = Depends(get_db)):
    hashed_password = hash_password(request.password)
    new_user = models.User(username=request.username,role = request.role, email=request.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def show(id:int, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with the id {id} is not available")
    return user

def update(id:int, request: schemas.User, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with the id {id} is not available")
    
    request.password = hash_password(request.password)
    user.update(request.dict())
    db.commit()
    return "Updated"



def get_favorite_products(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
    
    return user.favorites

def get_user_orders(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
    
    return user.orders


def delete(id:int, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with the id {id} is not available")
    
    user.delete(synchronize_session=False)
    db.commit()
    return "Deleted"

def create_order_item(user_id: int, request: schemas.OrderItemCreate, db: Session):
    product = db.query(models.Product).filter(models.Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if product.quantity < request.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient product quantity")

    # Update product quantity
    product.quantity -= request.quantity

    new_order_item = models.OrderItem(
        user_id=user_id,  # Associate order item with the current user
        product_id=request.product_id,
        quantity=request.quantity,
        unit_price=request.unit_price,
        total_price=request.total_price
    )
    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)
    return new_order_item

def get_order_item(user_id: int, id: int, db: Session):
    order_item = db.query(models.OrderItem).filter(models.OrderItem.id == id, models.OrderItem.user_id == user_id).first()
    if not order_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
    return order_item

def update_order_item(user_id: int, id: int, request: schemas.OrderItemCreate, db: Session):
    order_item = db.query(models.OrderItem).filter(models.OrderItem.id == id, models.OrderItem.user_id == user_id).first()
    if not order_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")

    product = db.query(models.Product).filter(models.Product.id == request.product_id).first()
    if not product or product.quantity < request.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient product quantity")

    order_item.product_id = request.product_id
    order_item.quantity = request.quantity
    order_item.unit_price = request.unit_price
    order_item.total_price = request.total_price
    db.commit()
    db.refresh(order_item)
    return order_item

def delete_order_item(user_id: int, id: int, db: Session):
    order_item = db.query(models.OrderItem).filter(models.OrderItem.id == id, models.OrderItem.user_id == user_id).first()
    if not order_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
    db.delete(order_item)
    db.commit()
    return "Order item deleted"