# this is the admin router
from ..repository import Admin
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..utils.database import get_db
from ..schemas import schemas
from typing import List
from ..utils.dependencies import is_admin, is_self_or_admin
from ..models import models
from ..utils import keycloak
import httpx
from fastapi import HTTPException, Depends,status


router = APIRouter(
    prefix="/admin",
    tags=["Admins"]
)

@router.get("/", response_model=List[schemas.Admin], dependencies=[Depends(keycloak.has_role("admin"))])
def get_all_admins(db: Session = Depends(get_db)):
    return Admin.get_all_admins(db)

# @router.post("/", response_model=schemas.Admin, dependencies=[Depends(is_admin)])
# def create_admin(request: schemas.UserCreate, db: Session = Depends(get_db)):
#     return Admin.create_admin(request, db)

# , dependencies=[Depends(keycloak.has_role("admin"))]
@router.post("/create", dependencies=[Depends(keycloak.has_role("admin"))])
async def create_admin(admin_request: schemas.UserCreate,db: Session = Depends(get_db)):
    token = await keycloak.get_keycloak_admin_token()
    
    async with httpx.AsyncClient() as client:
        # Check if user already exists
        response = await client.get(
            f"{keycloak.KEYCLOAK_URL}/admin/realms/{keycloak.REALM_NAME}/users",
            headers={"Authorization": f"Bearer {token}"},
            params={"username": admin_request.username}
        )
        response.raise_for_status()
        if response.json():
            raise HTTPException(status_code=409, detail="User already exists")

        # Create user in Keycloak
        response = await client.post(
            f"{keycloak.KEYCLOAK_URL}/admin/realms/{keycloak.REALM_NAME}/users",
            json={
                "username": admin_request.username,
                "enabled": True,
                "email": admin_request.email,
                "firstName": admin_request.firstname,
                "lastName": admin_request.lastname,
                "credentials": [{"type": "password", "value": admin_request.password, "temporary": False}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
    
        # Get the user ID
        user_id = response.headers["Location"].split("/")[-1]
    
        # Fetch the admin role ID
        response = await client.get(
            f"{keycloak.KEYCLOAK_URL}/admin/realms/{keycloak.REALM_NAME}/roles",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        roles = response.json()
        admin_role = next((role for role in roles if role["name"] == "admin"), None)
        if not admin_role:
            raise HTTPException(status_code=404, detail="Admin role not found")
        admin_role_id = admin_role["id"]
    
        # Assign the "admin" role to the user
        response = await client.post(
            f"{keycloak.KEYCLOAK_URL}/admin/realms/{keycloak.REALM_NAME}/users/{user_id}/role-mappings/realm",
            json=[{"id": admin_role_id, "name": "admin"}],
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
    
    return Admin.create_admin(admin_request, db)

@router.get("/orders", response_model=List[schemas.Order], dependencies=[Depends(keycloak.has_role("admin"))])
def get_all_orders(db: Session = Depends(get_db), current_admin: models.User = Depends(keycloak.get_current_user)):
    admin_id = db.query(models.User).filter(models.User.username == current_admin.username).first().id
    print(admin_id)
    return Admin.get_all_orders(admin_id,db)

@router.get("/{id}", response_model=schemas.Admin, dependencies=[Depends(keycloak.has_role("admin"))])
def show_admin(id: int, db: Session = Depends(get_db)):
    return Admin.show_admin(id, db)

@router.put("/{id}", response_model=str, dependencies=[Depends(keycloak.has_role("admin"))])
def update_admin(id: int, request: schemas.User, db: Session = Depends(get_db), current_user: models.User = Depends(is_self_or_admin)):
    return Admin.update_admin(id, request, db)

@router.delete("/{id}", response_model=str, dependencies=[Depends(keycloak.has_role("admin"))])
def delete_admin(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(is_self_or_admin)):
    return Admin.delete_admin(id, db)

@router.post("/products/", response_model=schemas.Product, dependencies=[Depends(keycloak.has_role("admin"))])
def create_product(request: schemas.ProductCreate, db: Session = Depends(get_db), current_admin: models.User = Depends(keycloak.get_current_user)):
    admin_id = db.query(models.User).filter(models.User.username == current_admin.username).first().id
    print(admin_id)
    return Admin.create_product(request, db, admin_id)

@router.get("/products/{id}", response_model=schemas.Product, dependencies=[Depends(keycloak.has_role("admin"))])
def get_product(id: int, db: Session = Depends(get_db)):
    return Admin.get_product(id, db)

@router.put("/products/{id}", response_model=schemas.Product, dependencies=[Depends(keycloak.has_role("admin"))])
def update_product(id: int, request: schemas.ProductCreate, db: Session = Depends(get_db)):
    return Admin.update_product(id, request, db)

@router.delete("/products/{id}", response_model=str, dependencies=[Depends(keycloak.has_role("admin"))])
def delete_product(id: int, db: Session = Depends(get_db)):
    return Admin.delete_product(id, db)

@router.get("/adminproducts/allproducts", response_model=List[schemas.Product], dependencies=[Depends(keycloak.has_role("admin"))])
def get_products_by_admin(db: Session = Depends(get_db),current_admin: models.User = Depends(keycloak.get_current_user)):
    admin_id = db.query(models.User).filter(models.User.username == current_admin.username).first().id
    print(admin_id)
    return Admin.get_products_by_admin(admin_id, db)
                        
