from sqladmin import Admin
from fastapi import FastAPI
from config import settings
from .auth import AdminAuthentication
from .views import (
    OrderAdmin,
    ProductAdmin,
    StoreAdmin,
    UserAdmin,
    UserRefreshAdmin,
)
from database.connection import async_engine

def admin_setup(app: FastAPI):
    authentication_backend = AdminAuthentication(secret_key=settings.SECRET_KEY)
    admin = Admin(
        engine=async_engine,
        app=app,
        authentication_backend=authentication_backend,
    )
    admin.add_model_view(UserAdmin)
    admin.add_model_view(UserRefreshAdmin)
    admin.add_model_view(StoreAdmin)
    admin.add_model_view(ProductAdmin)
    admin.add_model_view(OrderAdmin)