from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import date, datetime 
from .models import CategoryChoices, StatusChoices


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserRefreshScheme(BaseModel):
    refresh_token: str 

class UserLoginScheme(BaseModel):
    username: str 
    password: str

class UserResponseScheme(ORMModel):
    id: int 
    username: str
    email: EmailStr | None
    phone: int | None
    registered_date: date

class UserCreateScheme(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr | None = None 
    phone: int | None = None 
    password: str = Field(min_length=6, max_length=128)

class UserUpdateScheme(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=30)
    email: EmailStr | None = None 
    phone: int | None = None 
    password: str | None = Field(default=None, min_length=6, max_length=128)


class StoreResponseScheme(ORMModel):
    id: int
    name: str 
    category: CategoryChoices | None
    description: str | None
    image: str | None
    owner: int
    created_date: date

class StoreCreateScheme(BaseModel):
    name: str = Field(min_length=1, max_length=32)
    category: CategoryChoices = Field(default=CategoryChoices.CUSTOM)
    description: str | None = Field(default=None, max_length=1024)
    image: str | None = None

class StoreUpdateScheme(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=32)
    category: CategoryChoices | None = None 
    description: str | None = Field(default=None, max_length=1024)
    image: str | None = None


class ProductResponseScheme(ORMModel):
    id: int 
    store: int 
    name: str 
    price: str 
    created_date: date

class ProductCreateScheme(BaseModel):
    store: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=32)
    price: str = Field(min_length=1)

class ProductUpdateScheme(BaseModel):
    store: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=32)
    price: str | None = Field(default=None, min_length=1)


class OrderResponseScheme(ORMModel):
    id: int 
    product: int 
    user: int 
    status: StatusChoices | None
    ordered_date: datetime

class OrderCreateScheme(BaseModel):
    model_config = ConfigDict(extra='forbid')

    product: int = Field(gt=0)