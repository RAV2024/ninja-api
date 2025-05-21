from ninja import Router
from ninja.security import HttpBearer
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from ..schemas import UserOut, ErrorOut
from typing import List


class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        print(f"AUTHTOKEN: {token}")
        try:
            token_obj = Token.objects.get(key=token)
            request.user = token_obj.user
            return token
        except Token.DoesNotExist:
            return None

user_router = Router(tags=["users"])
auth = TokenAuth()


@user_router.get("/users/", response={200: List[UserOut], 403: ErrorOut}, auth=auth, summary="Получить список пользователей (только для менеджеров)")
def list_users(request):
    """Получить список пользователей (только для менеджеров)"""
    user = request.user
    if not user.groups.filter(name="менеджеры").exists():
        return 403, {"detail": "Доступ только для менеджеров!"}
    qs = User.objects.all()
    return qs