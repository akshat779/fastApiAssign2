from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..utils.oauth import get_current_user
from ..models import models
from ..utils.database import get_db

def get_user_by_id(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def is_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
    return current_user

def is_self_or_admin(user_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == models.RoleEnum.admin:
        return current_user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
    return current_user 