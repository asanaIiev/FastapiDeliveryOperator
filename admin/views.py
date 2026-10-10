from sqladmin import ModelView, Admin
from database.models import *

class UserAdmin(ModelView, model=UserProfile):
    column_list = [i.key for i in UserProfile.__mapper__.columns]

class UserRefreshAdmin(ModelView, model=UserRefresh):
    column_list = []

    for i in UserRefresh.__mapper__.columns:
        column_list.append(i.key)

class OrderAdmin(ModelView, model=Order):
    column_list = [i.key for i in Order.__mapper__.columns]

class ProductAdmin(ModelView, model=Product):
    column_list = '__all__'

class StoreAdmin(ModelView, model=Store):
    column_list = '__all__'