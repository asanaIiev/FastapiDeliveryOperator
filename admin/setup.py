from sqladmin import Admin
from fastapi import FastAPI
from .views import *
from database.connection import async_engine

def admin_setup(app: FastAPI):
    admin = Admin(engine=async_engine, app=app)
    admin.add_model_view(UserAdmin)
    admin.add_model_view(UserRefreshAdmin)
    admin.add_model_view(StoreAdmin)
    admin.add_model_view(ProductAdmin)
    admin.add_model_view(OrderAdmin)