from functools import wraps
from ninja.errors import HttpError


def permission_required(check_func):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            if not user or not check_func(user):
                raise HttpError(403, "Нет доступа")
            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def is_staff(user):
    return user.is_staff


def is_manager(user):
    return user.groups.filter(name='менеджеры').exists()
