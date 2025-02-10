from src.utils.database import get_db
from src.models import models
from fastapi import FastAPI
from src.utils.database import engine
from src.routes import UserRouter, AdminRouter, auth, OrderItemRouter
# from src.routes import firstAdmin

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(UserRouter.router)
app.include_router(AdminRouter.router)
app.include_router(auth.router)
app.include_router(OrderItemRouter.router)
# app.include_router(firstAdmin.router)