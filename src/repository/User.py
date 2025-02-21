from ..models import models
from ..schemas import schemas
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..utils.database import get_db
from fastapi import Depends
from ..utils.hashing import hash_password



def getAll(limit:int,offset:int,db:Session = Depends(get_db)):
    users = db.query(models.User).offset(offset).limit(limit).all()
    return users

def create(request: schemas.UserCreate, db:Session = Depends(get_db)):
    hashed_password = hash_password(request.password)
    new_user = models.User(username=request.username,role = request.role, email=request.email, password=hashed_password, firstname=request.firstname, lastname=request.lastname)
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
    
    favorite_products = [favorite.product.name for favorite in user.favorites]
    return favorite_products

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



# def create_order_item(user_id: int, request: schemas.OrderItemCreate, db: Session):
#     product = db.query(models.Product).filter(models.Product.id == request.product_id).first()
#     if not product:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
#     if product.quantity < request.quantity:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient product quantity")

#     # Calculate prices
#     unit_price = product.price
#     total_price = unit_price * request.quantity

#     # Update product quantity
#     product.quantity -= request.quantity

#     new_order_item = models.OrderItem(
#         user_id=user_id,  # Add user_id
#         order_id=None,  # This should be set to the actual order ID when creating an order
#         product_id=request.product_id,
#         quantity=request.quantity,
#         unit_price=unit_price,
#         total_price=total_price
#     )

#     db.add(new_order_item)
#     db.commit()
#     db.refresh(new_order_item)
#     return new_order_item

def create_order_item(user_id: int, request: schemas.OrderItemCreate, db: Session):
    product = db.query(models.Product).filter(models.Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if product.quantity < request.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient product quantity")

    
    unit_price = product.price
    total_price = unit_price * request.quantity

   
    product.quantity -= request.quantity

  
    order = db.query(models.Order).filter(models.Order.user_id == user_id, models.Order.status == 'pending').first()
    if not order:
        order = models.Order(user_id=user_id, total_quantity=0, total_amount=0, status='pending')
        db.add(order)
        db.commit()
        db.refresh(order)

    new_order_item = models.OrderItem(
        user_id=user_id,
        order_id= order.id,  
        product_id=request.product_id,
        quantity=request.quantity,
        unit_price=unit_price,
        total_price=total_price
    )

   
    order.total_quantity += request.quantity
    order.total_amount += total_price

    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)
    return new_order_item

# def get_order_item(user_id: int, order_item_id: int, db: Session):
#     order_item = db.query(models.OrderItem).filter(models.OrderItem.id == order_item_id, models.OrderItem.user_id == user_id).first()
#     if not order_item:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found")
#     return order_item

# def get_order_item(user_id: int, db: Session):
#     order_items = db.query(models.OrderItem).filter(models.OrderItem.user_id == user_id).all()
#     print(order_items)
#     if not order_items:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No order items found for this user")
#     return order_items

def add_favorite_product(user_id: int, request: schemas.FavoriteCreate, db: Session):
    product = db.query(models.Product).filter(models.Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    favorite = db.query(models.Favorite).filter(models.Favorite.user_id == user_id, models.Favorite.product_id == request.product_id).first()
    if favorite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product already added to favorites")

    new_favorite = models.Favorite(user_id=user_id, product_id=request.product_id)
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    return product

def get_order_items_by_order_id(user_id: int, db: Session):
    order_items = db.query(models.OrderItem).filter(models.OrderItem.user_id == user_id).all()
    if not order_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No order items found for this order")
    return order_items

def get_order_items_by_user_id(user_id: int, db: Session,limit:int,offset:int):
    order_items = db.query(models.OrderItem).filter(models.OrderItem.user_id == user_id).offset(offset).limit(limit).all()
    if not order_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No order items found for this user")
    return order_items

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

def create_order(user_id: int, db: Session):
    order_items = db.query(models.OrderItem).filter(models.OrderItem.user_id == user_id).all()
    if not order_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No order items to place an order")

    total_quantity = sum(item.quantity for item in order_items)
    total_amount = sum(item.total_price for item in order_items)

    order = models.Order(
        user_id=user_id,
        total_quantity=total_quantity,
        total_amount=total_amount,
        status="placed"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Assign order_id to order items and update order items
    for item in order_items:
        item.order_id = order.id
        db.add(item)
    db.commit()

    # Query the order again to include the order items in the response
    order_with_items = db.query(models.Order).filter(models.Order.id == order.id).first()

    # Clear order items
    for item in order_items:
        db.delete(item)
    db.commit()

    return order_with_items

def get_all_orders(user_id: int, db: Session,limit:int,offset:int):
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).offset(offset).limit(limit).all()
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No orders found for this user")
    return orders