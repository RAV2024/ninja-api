from ninja import Router
from ninja.security import HttpBearer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from ..models import Order, OrderItem, OrderStatus, Product, WishlistItem
from ..schemas import OrderOut, OrderItemIn, OrderItemOut, OrderIn, StatusOut, ErrorOut

from typing import List, Union
from decimal import Decimal
from datetime import datetime



class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            token_obj = Token.objects.get(key=token)
            request.user = token_obj.user
            return token
        except Token.DoesNotExist:
            return None



order_router = Router(tags=["orders"])
auth = TokenAuth()

@order_router.get("/", response={200: List[OrderOut], 403: ErrorOut}, auth = auth, summary="Список всех заказов (только менеджер)")
def get_all_orders(request):
    """Получить список всех заказов (только для менеджеров)"""
    if not request.user.groups.filter(name="менеджеры").exists():
        return 403, {"detail": "Только для менеджеров!"}
    return Order.objects.all().prefetch_related("items__product")


@order_router.get("/my", response=List[OrderOut], auth=auth, summary="Список заказов текущего пользователя")
def get_my_orders(request):
    return Order.objects.filter(user=request.user).prefetch_related("items__product")



@order_router.get("/user/{user_id}", response={200: List[OrderOut], 403: ErrorOut, 404: ErrorOut}, auth=auth, summary="Список заказов по ID пользователя (только менеджер)")
def get_user_orders(request, user_id: int):
    """Список заказов по ID пользователя (только для менеджеров)"""
    if not request.user.groups.filter(name="менеджеры").exists():
        return 403, {"detail": "Доступ только для менеджеров!"}

    target_user = get_object_or_404(User, id=user_id)
    return Order.objects.filter(user=target_user).prefetch_related("items__product")


@order_router.post("/", response={200: OrderOut, 400: ErrorOut}, auth=auth, summary="Создать заказ из Wishlist текущего пользователя")
def create_order_from_wishlist(request):
    wishlist = WishlistItem.objects.filter(user=request.user)

    if not wishlist.exists():
        return 400, {"detail": "Вишлист пуст!"}

    try:
        status = OrderStatus.objects.get(name="Новый")
    except OrderStatus.DoesNotExist:
        return 400, {"detail": "Статус 'Новый' не найден"}

    order = Order.objects.create(user=request.user, status=status, total=0)

    total = Decimal('0.00')
    for item in wishlist:
        item_total = item.product.price * item.quantity
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            cost=item_total,
        )
        total += item_total

    order.total = total
    order.save()

    # Очистить wishlist
    wishlist.delete()

    return order

@order_router.put("/{order_id}/status", response={200: OrderOut, 403: ErrorOut, 404: ErrorOut}, auth=auth, summary="Изменить статус заказа (только менеджер)")
def update_order_status(request, order_id: int, status_id: int):
    """Изменить статус заказа (только менеджер)"""
    if not request.user.groups.filter(name="менеджеры").exists():
        return 403, {"detail": "Только менеджеры могут менять статус"}

    order = get_object_or_404(Order, id=order_id)
    status = get_object_or_404(OrderStatus, id=status_id)

    order.status = status
    order.save()

    return order