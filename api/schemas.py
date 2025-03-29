from ninja import Schema
from typing import Optional

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