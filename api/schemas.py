from ninja import Schema
from typing import Optional


class RegisterIn(Schema):
    username: str
    password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    email: Optional[str] = ""
    is_manager: Optional[bool] = False


class LoginIn(Schema):
    username: str
    password: str

class LoginOut(Schema):
    token: str


class ErrorOut(Schema):
    detail: str

class UserOut(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str

    class Config:
        orm_mode = True


class CategoryIn(Schema):
    title: str
    slug: str

class CategoryOut(Schema):
    id: int
    title: str
    slug: str

    class Config:
        orm_mode = True



class ProductIn(Schema):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class ProductOut(Schema):
    id: int
    title: str
    category_id: int
    description: str
    price: float

    class Config:
        orm_mode = True


class ProductFilter(Schema):
    min_price: Optional[float]
    max_price: Optional[float]
    title: Optional[str]
    description: Optional[str]