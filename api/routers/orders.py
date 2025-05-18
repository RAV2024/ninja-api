from django.db import transaction
from ninja import Router
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from ninja.security import HttpBearer
from ..models import Order, OrderItem, OrderStatus, Product
from ..schemas import OrderOut, OrderItemIn, OrderItemOut, OrderIn, StatusOut, ErrorOut
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from typing import List, Union
from decimal import Decimal


class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            token_obj = Token.objects.get(key=token)
            request.user = token_obj.user
            return token
        except Token.DoesNotExist:
            return None

auth = TokenAuth()
order_router = Router(tags=["orders"])


@order_router.get("/", response={200: List[OrderOut], 403: ErrorOut}, auth=auth,summary="Просмотр всех заказов (только для менеджеров)")
def list_orders(request):
    """Просмотр всех заказов (только для менеджеров)"""
    if not request.user.groups.filter(name="менеджеры").exists():
        raise HttpError(403, "Доступ только для менеджеров!")
    return Order.objects.all().order_by("-created_at")


@order_router.get("/my", response=List[OrderOut], auth=auth, summary="Список заказов текущего пользователя")
def my_orders(request):
    return Order.objects.filter(user=request.user).order_by("-created_at")



@order_router.post("/create", response=Union[OrderOut, ErrorOut], auth=auth, summary="Создать заказ с продуктами и расчётом стоимости")
@transaction.atomic
def create_order(request, items: List[OrderItemIn]):
    order = Order.objects.create(
        user=request.user,
        status=OrderStatus.objects.get(pk=1),  # статус "Новый"
        total=0
    )

    total = Decimal("0.00")

    for item in items:
        product = get_object_or_404(Product, id=item.product)
        cost = product.price * item.quantity

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item.quantity,
            cost=cost
        )
        total += cost

    order.total = total
    order.save()

    return Order.objects.prefetch_related("items__product__category", "status").get(id=order.id)



@order_router.put("/status/{order_id}", response={200: OrderOut, 400: ErrorOut, 403: ErrorOut, 404: ErrorOut},auth=auth, summary="Изменить статус заказа (только менеджер)")
def update_order_status(request, order_id: int, status_id: int):
    """Изменить статус заказа (только менеджер)"""

    if not request.user.groups.filter(name="менеджеры").exists():
        raise HttpError(403, "Доступ только для менеджеров!")

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        raise HttpError(404, "Заказ не найден")

    try:
        new_status = OrderStatus.objects.get(id=status_id)
    except OrderStatus.DoesNotExist:
        raise HttpError(400, "Недопустимый статус")

    order.status = new_status
    order.save()
    return order








