from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..utils.database import get_db
from ..utils.hashing import hash_password
from ..models import models
from ..schemas import schemas

router = APIRouter()

@router.post("/create-first-admin", response_model=schemas.User)
def create_first_admin(db: Session = Depends(get_db)):
    hashed_password = hash_password("adminpassword")
    new_user = models.User(
        username="admin",
        email="admin@example.com",
        password_hash=hashed_password,
        role=models.RoleEnum.admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    new_admin = models.Admin(user_id=new_user.id)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_user