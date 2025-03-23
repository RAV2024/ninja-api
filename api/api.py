from ninja import NinjaAPI, Schema, Field
from ninja import UploadedFile, File
from django.shortcuts import get_object_or_404
from typing import List
from .models import Category, Product
from typing import Optional


api = NinjaAPI()


class CategoryIn(Schema):
    title: str
    slug: str


class CategoryOut(Schema):
    id: int
    title: str
    slug: str


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


@api.get("/categories", response=List[CategoryOut])
def list_categories(request):
    return Category.objects.all()


@api.post("/categories", response=CategoryOut)
def create_category(request, category: CategoryIn):
    new_category = Category.objects.create(**category.dict())
    return new_category


@api.get("/categories/{slug}", response=CategoryOut)
def get_category(request, slug: str):
    return get_object_or_404(Category, slug=slug)


@api.delete("/categories/{slug}")
def delete_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    category.delete()
    return {"success": True}


@api.get("/categories/{slug}/products", response=List[ProductOut])
def get_products_in_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    return category.products.all()



#-------------------------------------------------------------


@api.get("/products", response=List[ProductOut])
def list_products(request):
    return Product.objects.all()


@api.post("/products", response={201: ProductOut, 404: dict})
def create_product(request, payload: ProductIn):
    category = Category.objects.filter(slug=payload.category).first()
    if not category:
        return 404, {"error": "Category not found"}

    product = Product.objects.create(
        title=payload.title,
        category=category,
        description=payload.description,
        price=payload.price
    )
    return 201, product



@api.get("/products/{product_id}", response={200: ProductOut, 404: dict})
def get_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    return product



@api.patch("/products/{product_id}", response={200: ProductOut, 404: dict})
def update_product(request, product_id: int, payload: ProductIn):
    product = get_object_or_404(Product, id=product_id)

    if payload.category:
        category = Category.objects.filter(slug=payload.category).first()
        if not category:
            return 404, {"error": "Category not found"}
        product.category = category

    if payload.title:
        product.title = payload.title
    if payload.description:
        product.description = payload.description
    if payload.price is not None:
        product.price = payload.price

    product.save()
    return product



@api.delete("/products/{product_id}")
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return {"success": True}