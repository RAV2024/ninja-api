from ninja import Router
from django.contrib.auth.models import User
from .auth_backend import auth
from ..schemas import UserOut, ErrorOut
from typing import List
from ..models import ManagerRequest
from .permissions import permission_required, is_manager

user_router = Router(tags=["users"])


@user_router.get("/users/", response={200: List[UserOut], 403: ErrorOut}, auth=auth, summary="Получить список пользователей (Менеджер)")
@permission_required(is_manager)
def list_users(request):
    """Получить список пользователей (только для менеджеров)"""
    qs = User.objects.all()
    return qs


@user_router.post("/request-manager", response={200: dict, 400: ErrorOut}, auth=auth, summary="Подать заявку на стать менеджером")
def request_manager(request):
    user = request.user

    if user.groups.filter(name='менеджеры').exists():
        return 400, {"detail": "Вы уже являетесь менеджером."}

    existing_request = ManagerRequest.objects.filter(user=user, status='ожидает рассмотрения').first()
    if existing_request:
        return 400, {"detail": "Заявка уже подана и находится в ожидании."}

    ManagerRequest.objects.create(user=user)
    return {"message": "Ваша заявка принята. Ожидайте подтверждения."}