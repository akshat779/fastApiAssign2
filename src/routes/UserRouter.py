from ..repository import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..utils.database import get_db
from ..schemas import schemas
from typing import List
from ..utils.dependencies import is_self_or_admin
from ..models import models
from ..utils.oauth import get_current_user
from ..utils import keycloak
import httpx

router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

@router.get("/", response_model=List[schemas.User])
def getAll(db: Session = Depends(get_db)):
    return User.getAll(db)

# @router.post("/create", response_model=schemas.User)
# def create(request: schemas.UserCreate, db: Session = Depends(get_db)):
#     return User.create(request, db)

@router.post("/create")
async def create_user(user_request: schemas.UserCreate,db: Session = Depends(get_db)):
    token = await keycloak.get_keycloak_admin_token()
    
    async with httpx.AsyncClient() as client:
        # Check if user already exists
        response = await client.get(
            f"{keycloak.KEYCLOAK_URL}/admin/realms/{keycloak.REALM_NAME}/users",
            headers={"Authorization": f"Bearer {token}"},
            params={"username": user_request.username}
        )
        response.raise_for_status()
        if response.json():
            raise HTTPException(status_code=409, detail="User already exists")

        # Create user in Keycloak
        response = await client.post(
            f"{keycloak.KEYCLOAK_URL}/admin/realms/{keycloak.REALM_NAME}/users",
            json={
                "username": user_request.username,
                "enabled": True,
                "email": user_request.email,
                "firstName": user_request.firstname,
                "lastName": user_request.lastname,
                "credentials": [{"type": "password", "value": user_request.password, "temporary": False}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
    
    return User.create(user_request, db)
    # return {"message": "User created successfully"}


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

# @router.get("/order-items", response_model=List[schemas.OrderItem])
# def get_order_items(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     print(current_user.id)
#     return User.get_order_item(current_user.id, db)
# @router.get("/order-items/{id}", response_model=schemas.OrderItem)
# def get_order_item(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     return User.get_order_items(current_user.id, db)

@router.put("/order-items/{id}", response_model=schemas.OrderItem)
def update_order_item(id: int, request: schemas.OrderItemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return User.update_order_item(current_user.id, id, request, db)

# @router.get("/order-items/{id}", response_model=schemas.OrderItem)
# def get_order_item(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     return User.get_order_item(current_user.id, id, db)
@router.get("/orders/{order_id}/order-items", response_model=List[schemas.OrderItem])
def get_order_items_by_order_id(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return User.get_order_items_by_order_id(current_user.id, order_id, db)
# @router.get("/{user_id}/order-items", response_model=List[schemas.OrderItem])
# def get_order_items_by_user_id(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(is_self_or_admin)):
#     return User.get_order_items_by_user_id(user_id, db)

@router.post("/orders/", response_model=schemas.Order)
def create_order(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return User.create_order(current_user.id, db)

@router.get("/{user_id}/all-orders", response_model=List[schemas.Order])
def get_all_orders(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(is_self_or_admin)):
    return User.get_all_orders(user_id, db)