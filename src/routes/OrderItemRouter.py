from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..utils.database import get_db
from ..schemas import schemas
from ..repository import OrderItem
from typing import List

router = APIRouter(
    prefix="/order-items",
    tags=["products"]
)



@router.get("/products/", response_model=List[schemas.Product])
def get_all_products(db: Session = Depends(get_db)):
    return OrderItem.get_all_products(db)
