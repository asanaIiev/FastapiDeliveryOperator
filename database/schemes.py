from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from datetime import date, datetime 

class UserRefreshScheme(BaseModel):
    refresh_token: str 

class UserLoginScheme(BaseModel):
    username: str 
    password: str

class UserResponseScheme(BaseModel):
    id: int 
    username: str
    email: EmailStr
    phone: int
    registered_date: date

class UserCreateScheme(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    email: EmailStr | None = None 
    phone: str | None = None 
    password: str = Field(min_length=6, max_length=128)

class UserUpdateScheme(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=32)
    email: EmailStr | None = None 
    phone: str | None = None 
    password: str | None = Field(default=None, min_length=6, max_length=128)


class CategoryChoices(str, Enum):
    CUSTOM = 'Custom'
    ELECTRONICS = 'Electronics'
    BEAUTY = 'Beauty'
    CLOTHING = 'Clothing'
    FOOD = 'Food'

class StoreResponseScheme(BaseModel):
    id: int
    name: str 
    category: CategoryChoices
    description: str 
    image: str 
    owner: int
    created_date: date

class StoreCreateScheme(BaseModel):
    name: str = Field(min_length=32)
    category: CategoryChoices = Field(default='Custom')
    description: str | None = Field(default=None, max_length=1024)
    image: str | None = None

class StoreUpdateScheme(BaseModel):
    name: str | None = Field(default=None, max_length=32)
    category: CategoryChoices | None = None 
    description: str | None = Field(default=None, max_length=1024)
    image: str | None = None


class ProductResponseScheme(BaseModel):
    id: int 
    store: int 
    name: str 
    price: str 
    created_date: date

class ProductCreateScheme(BaseModel):
    store: int = Field(gt=0)
    name: str = Field(max_length=32)
    price: str = Field(min_length=1)

class ProductUpdateScheme(BaseModel):
    store: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, max_length=32)
    price: str | None = Field(default=None, min_length=1)


class StatusChoices(str, Enum):
    CANCEL = 'Cancel'
    CONFIRM = 'Confirm'
    PENDING = 'Pending'
    DELIVERED = 'Delivered'

class OrderResponseScheme(BaseModel):
    id: int 
    product: int 
    user: int 
    status: StatusChoices
    ordered_date: datetime

class OrderCreateScheme(BaseModel):
    product: int = Field(gt=0)
    status: StatusChoices = Field(default='Pending')