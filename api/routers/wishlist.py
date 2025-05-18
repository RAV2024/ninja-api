from ninja import Router
from ninja.security import HttpBearer
from django.shortcuts import get_object_or_404
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