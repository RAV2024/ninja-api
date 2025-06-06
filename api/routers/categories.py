from ninja import Router, Body
from typing import List
from django.shortcuts import get_object_or_404
from ..models import Category
from ..schemas import CategoryOut, CategoryIn, ProductOut, CategoryUpdate, ErrorOut
from .auth_backend import auth
from .permissions import permission_required, is_manager

category_router = Router(tags=["categories"])


@category_router.get("/", response={200: List[CategoryOut], 403: ErrorOut}, summary='Получить список категорий')
def list_categories(request):
    return Category.objects.all()


@category_router.get("/{slug}", response=CategoryOut, summary='Получить категорию по slug')
def get_category(request, slug: str):
    return get_object_or_404(Category, slug=slug)


@category_router.get("/{slug}/products", response=List[ProductOut], summary='Получить продукты по категории')
def get_products_in_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    return category.products.all()


@category_router.post("/", response=CategoryOut, auth=auth, summary='Добавить категорию (Менеджер)')
@permission_required(is_manager)
def create_category(request, category: CategoryIn):
    new_category = Category.objects.create(title=category.title, slug=category.slug)
    return new_category


@category_router.patch("/{slug}", response=CategoryOut, auth=auth, summary='Обновить категорию (Менеджер)')
@permission_required(is_manager)
def partial_update_category(request, slug: str, data: CategoryUpdate = Body(...)):
    category = get_object_or_404(Category, slug=slug)
    if data.title is not None:
        category.title = data.title
    if data.slug is not None:
        category.slug = data.slug
    category.save()
    return category


@category_router.delete("/{slug}", auth=auth, summary='Удалить категорию (Менеджер)')
@permission_required(is_manager)
def delete_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    if not category:
        return 404, {"detail": "Категория не найдена"}
    category.delete()
    return {"success": True}
