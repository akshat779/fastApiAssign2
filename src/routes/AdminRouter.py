# this is the admin router
from ..repository import Admin
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..utils.database import get_db
from ..schemas import schemas
from typing import List
from ..utils.dependencies import is_admin, is_self_or_admin
from ..models import models


router = APIRouter(
    prefix="/admin",
    tags=["Admins"]
)

@router.get("/", response_model=List[schemas.Admin], dependencies=[Depends(is_admin)])
def get_all_admins(db: Session = Depends(get_db)):
    return Admin.get_all_admins(db)

@router.post("/", response_model=schemas.Admin, dependencies=[Depends(is_admin)])
def create_admin(request: schemas.UserCreate, db: Session = Depends(get_db)):
    return Admin.create_admin(request, db)

@router.get("/{id}", response_model=schemas.Admin, dependencies=[Depends(is_admin)])
def show_admin(id: int, db: Session = Depends(get_db)):
    return Admin.show_admin(id, db)

@router.put("/{id}", response_model=str, dependencies=[Depends(is_admin)])
def update_admin(id: int, request: schemas.User, db: Session = Depends(get_db), current_user: models.User = Depends(is_self_or_admin)):
    return Admin.update_admin(id, request, db)

@router.delete("/{id}", response_model=str, dependencies=[Depends(is_admin)])
def delete_admin(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(is_self_or_admin)):
    return Admin.delete_admin(id, db)

@router.post("/products/", response_model=schemas.Product, dependencies=[Depends(is_admin)])
def create_product(request: schemas.ProductCreate, db: Session = Depends(get_db), current_admin: models.User = Depends(is_admin)):
    return Admin.create_product(request, db, admin_id=current_admin.id)

@router.get("/products/{id}", response_model=schemas.Product, dependencies=[Depends(is_admin)])
def get_product(id: int, db: Session = Depends(get_db)):
    return Admin.get_product(id, db)

@router.put("/products/{id}", response_model=schemas.Product, dependencies=[Depends(is_admin)])
def update_product(id: int, request: schemas.ProductCreate, db: Session = Depends(get_db)):
    return Admin.update_product(id, request, db)

@router.delete("/products/{id}", response_model=str, dependencies=[Depends(is_admin)])
def delete_product(id: int, db: Session = Depends(get_db)):
    return Admin.delete_product(id, db)

@router.get("/adminproducts/{admin_id}", response_model=List[schemas.Product], dependencies=[Depends(is_admin)])
def get_products_by_admin(admin_id: int, db: Session = Depends(get_db)):
    return Admin.get_products_by_admin(admin_id, db)
                        