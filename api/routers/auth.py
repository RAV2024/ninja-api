from ninja import Router
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..schemas import LoginIn, LoginOut, RegisterIn,  ErrorOut

auth_router = Router(tags=["auth"])

@auth_router.post("/login", response={200: LoginOut, 401: ErrorOut}, summary="Вход в систему")
def login(request, data: LoginIn):
    user = authenticate(username=data.username, password=data.password)
    if user is None:
        return 401, {"detail": "Неверные учетные данные"}
    token, _ = Token.objects.get_or_create(user=user)
    return {"token": token.key}



@auth_router.post("/register", response={200: LoginOut, 400: ErrorOut}, summary="Регистрация пользователя")
def register(request, data: RegisterIn):
    if User.objects.filter(username=data.username).exists():
        return 400, {"detail": "Пользователь с таким именем уже существует"}

    user = User.objects.create_user(
        username=data.username,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email
    )

    token, _ = Token.objects.get_or_create(user=user)
    return {"token": token.key}