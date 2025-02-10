from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas

def get_all_products(db: Session):
    products = db.query(models.Product).all()
    return products
