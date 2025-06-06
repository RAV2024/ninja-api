from django.contrib.auth.models import User, Group
from ninja import Router
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from .auth_backend import auth
from .permissions import permission_required, is_staff
from ..models import ManagerRequest
from ..schemas import ManagerOut, ErrorOut

admin_router = Router(tags=["admin"])



@admin_router.get("/manager-requests", response={200: list[ManagerOut]}, auth=auth, summary="Список заявок на менеджера")
@permission_required(is_staff)
def list_manager_requests(request, status: str = None):
    """
    Получить список заявок с возможностью фильтрации по статусу.
    Можно указать статус в параметре query_params: 'ожидает рассмотрения' или 'одобрен'.
    Если не указать, возвращаются все заявки.
    """
    allowed_statuses = ['ожидает рассмотрения', 'одобрен']
    if status and status not in allowed_statuses:
        return 400, {"detail": "Недопустимый статус фильтрации"}

    if status:
        requests_qs = ManagerRequest.objects.filter(status=status)
    else:
        requests_qs = ManagerRequest.objects.all()

    data = []
    for req in requests_qs:
        data.append(ManagerOut(
            id=req.id,
            user=req.user,
            status=req.status,
            created_at=req.created_at
        ))
    return data


@admin_router.post("/approve-manager/{request_id}", response={200: dict, 404: ErrorOut}, auth=auth, summary="Подтвердить заявку и повысить пользователя до менеджера")
@permission_required(is_staff)
def approve_manager_request(request, request_id: int):
    try:
        req_obj = ManagerRequest.objects.get(id=request_id, status='ожидает рассмотрения')
    except ManagerRequest.DoesNotExist:
        return 404, {"detail": "Запрос не найден или уже обработан"}

    user = req_obj.user

    group, _ = Group.objects.get_or_create(name='менеджеры')
    user.groups.add(group)

    req_obj.status = 'одобрен'
    req_obj.save()


    return {"message": f"Пользователь стал менеджером."}




