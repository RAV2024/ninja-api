from ninja import Router
from typing import List, Optional
from django.shortcuts import get_object_or_404

from ..models import Product, Category
from ..schemas import ProductIn, ProductOut, ProductFilter

product_router = Router(tags=["products"])


@product_router.get("/", response=List[ProductOut])
def list_products(
    request,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    title: Optional[str] = None,
    description: Optional[str] = None
):
    products = Product.objects.all()

    if min_price is not None:
        products = products.filter(price__gte=min_price)
    if max_price is not None:
        products = products.filter(price__lte=max_price)
    if title:
        products = products.filter(title__icontains=title)
    if description:
        products = products.filter(description__icontains=description)

    return products




@product_router.post("/", response={201: ProductOut, 404: dict})
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


@product_router.get("/{product_id}", response={200: ProductOut, 404: dict})
def get_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    return product


@product_router.patch("/{product_id}", response={200: ProductOut, 404: dict})
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


@product_router.delete("/{product_id}")
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return {"success": True}


