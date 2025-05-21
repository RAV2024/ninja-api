from ninja import Router
from ninja.security import HttpBearer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ..models import WishlistItem, Product
from ..schemas import WishlistItemOut, WishlistItemIn, ErrorOut
from rest_framework.authtoken.models import Token
from typing import List


class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            token_obj = Token.objects.get(key=token)
            request.user = token_obj.user
            return token
        except Token.DoesNotExist:
            return None

wishlist_router = Router(tags=["wishlist"])
auth = TokenAuth()


@wishlist_router.get("/", response=List[WishlistItemOut], auth=auth, summary='Получить вишлист текущего пользователя')
def get_wishlist(request):
    return WishlistItem.objects.filter(user=request.user)


@wishlist_router.get("/user/{user_id}", response={200: List[WishlistItemOut], 403: ErrorOut, 404: ErrorOut}, auth=auth, summary="Получить вишлист пользователя по ID (только для менеджеров)")
def get_user_wishlist_for_manager(request, user_id: int):
    """Получает вишлист пользователя по ID — только для менеджеров"""
    user = request.user
    if not user.groups.filter(name="менеджеры").exists():
        return 403, {"detail": "Доступ только для менеджеров!"}

    target_user = get_object_or_404(User, id=user_id)
    wishlist_items = WishlistItem.objects.filter(user=target_user)

    return wishlist_items


@wishlist_router.post("/", response={200: WishlistItemOut, 400: ErrorOut}, auth=auth, summary='Добавить товар в вишлист')
def add_to_wishlist(request, data: WishlistItemIn):
    product = get_object_or_404(Product, id=data.product_id)
    item, created = WishlistItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": data.quantity}
    )
    if not created:
        item.quantity += data.quantity
        item.save()

    item.product = product

    return item


@wishlist_router.delete("/{product_id}", response={200: dict, 404: ErrorOut}, auth=auth, summary='Удалить товар из вишлиста')
def remove_from_wishlist(request, product_id: int):
    try:
        item = WishlistItem.objects.get(user=request.user, product_id=product_id)
        item.delete()
        return {"success": True}
    except WishlistItem.DoesNotExist:
        return 404, {"detail": "Товар не найден в вишлисте"}


@wishlist_router.delete("/{product_id}/decrement", response={200: dict, 404: ErrorOut}, auth=auth, summary='Уменьшить количество товара в вишлисте на единицу')
def decrement_from_wishlist(request, product_id: int):
    try:
        item = WishlistItem.objects.get(user=request.user, product_id=product_id)
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
        return {"success": True}
    except WishlistItem.DoesNotExist:
        return 404, {"detail": "Товар не найден в вишлисте"}