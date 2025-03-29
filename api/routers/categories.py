from ninja import Router, Schema
from typing import List
from django.shortcuts import get_object_or_404
from ..models import Category
from ..schemas import CategoryOut, CategoryIn, ProductOut


category_router = Router(tags=["categories"])


@category_router.get("/", response=List[CategoryOut])
def list_categories(request):
    return Category.objects.all()


@category_router.post("/", response=CategoryOut)
def create_category(request, category: CategoryIn):
    new_category = Category.objects.create(title=category.title, slug=category.slug)
    return new_category


@category_router.get("/{slug}", response=CategoryOut)
def get_category(request, slug: str):
    return get_object_or_404(Category, slug=slug)


@category_router.delete("/{slug}")
def delete_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    category.delete()
    return {"success": True}

@category_router.get("/{slug}/products", response=List[ProductOut])
def get_products_in_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    return category.products.all()