from sqladmin import ModelView, Admin
from database.models import Order, Product, Store, UserProfile, UserRefresh

class UserAdmin(ModelView, model=UserProfile):
    column_list = [column.key for column in UserProfile.__mapper__.columns if column.key != 'password']
    column_details_list = column_list
    form_excluded_columns = ['password']

class UserRefreshAdmin(ModelView, model=UserRefresh):
    column_list = ['id', 'user_id']
    column_details_list = column_list
    form_excluded_columns = ['token']

class OrderAdmin(ModelView, model=Order):
    column_list = [i.key for i in Order.__mapper__.columns]

class ProductAdmin(ModelView, model=Product):
    column_list = '__all__'

class StoreAdmin(ModelView, model=Store):
    column_list = '__all__'